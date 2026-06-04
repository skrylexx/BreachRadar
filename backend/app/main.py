"""
BreachRadar WebUI — FastAPI Application Entry Point
====================================================
Main entry point. Configures middleware, routes, and lifecycle.
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import Base, engine
from app.core.init_db import initialize_database
from app.core.redis import redis_client
from app.engine.scheduler import ScanScheduler
from app.routers import (
    api_keys,
    auth,
    cve,
    health,
    intelligence,
    ransomlook,
    reports,
    scans,
    users,
    webhooks,
)
from app.routers import settings as settings_router
from app.routers.dashboard import router as dashboard_router

# ─── Global Rate Limiter ──────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ─── Lifecycle (startup / shutdown) ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Resource initialization and cleanup."""
    # Startup
    # Initialize the database (Schema + Admin)
    await initialize_database()

    # Start the background Scheduler
    scheduler = None
    if getattr(settings, "schedule_enabled", False):
        import logging
        logger = logging.getLogger("breachradar.scheduler")

        # Redis Lock to ensure only one worker starts the scheduler
        scheduler_lock_key = "breachradar:scheduler_lock"
        is_scheduler_leader = await redis_client.set(scheduler_lock_key, "1", nx=True, ex=60)

        if is_scheduler_leader:
            logger.info("Starting ScanScheduler (Leader Instance)...")

            async def _scan_callback():
                """Callback triggered by the scheduler for a full scan."""
                from datetime import datetime

                from app.core.database import AsyncSessionLocal
                from app.engine.logic import ScanManager
                from app.models.scan import ScanResult, ScanStatus

                async with AsyncSessionLocal() as db:
                    # 1. Create the ScanResult entry in DB
                    scan = ScanResult(
                        target_domain=settings.target_domain,
                        status=ScanStatus.RUNNING,
                        triggered_by="scheduler",
                        started_at=datetime.now(UTC),
                    )
                    db.add(scan)
                    await db.commit()
                    await db.refresh(scan)

                    # 2. Start the scan
                    scan_manager = ScanManager()
                    await scan_manager.run_full_scan(scan.id)

            async def _watch_callback():
                """Callback triggered by the scheduler for digital monitoring (CVE + RSS + GitHub)."""
                from app.core.database import AsyncSessionLocal
                from app.engine.cve_monitor import CVEMonitor
                from app.engine.intelligence_monitor import IntelligenceMonitor

                # Default categories to monitor for CVEs
                default_categories = ["nvd_windows", "nvd_linux", "osv_pypi", "osv_npm", "osv_go"]

                async with AsyncSessionLocal() as db:
                    # 1. CVE Monitoring (NVD, OSV...)
                    cve_monitor = CVEMonitor(db)
                    # 2. Digital Monitoring (RSS, GitHub...)
                    intel_monitor = IntelligenceMonitor(db)

                    try:
                        await asyncio.gather(
                            cve_monitor.poll_all(active_categories=default_categories),
                            intel_monitor.run_all(),
                        )
                    except Exception as e:
                        import logging

                        logger = logging.getLogger("breachradar.scheduler")
                        logger.error(f"Error during scheduled monitoring: {e}")
                    finally:
                        await cve_monitor.close()
                        await intel_monitor.close()

            scheduler = ScanScheduler(settings=settings, scan_callback=_scan_callback, cve_callback=_watch_callback)
            scheduler.start()

            # Background task to maintain the scheduler lock
            async def _maintain_scheduler_lock():
                while True:
                    await asyncio.sleep(30)
                    await redis_client.expire(scheduler_lock_key, 60)

            asyncio.create_task(_maintain_scheduler_lock())
        else:
            logger.debug("ScanScheduler already active on another instance.")

    yield

    # Shutdown
    if scheduler:
        scheduler.stop()
    await redis_client.aclose()
    await engine.dispose()


# ─── FastAPI Application ──────────────────────────────────────────────────────
app = FastAPI(
    title="BreachRadar WebUI API",
    description="Backend API of the BreachRadar WebUI — SOC Governance",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────

# Trusted Host — protection against Host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts if settings.environment == "production" else ["*"],
)

# CORS — allow only configured origins
# NOTE: Added AFTER TrustedHost to be executed BEFORE (LIFO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # Required for HttpOnly Cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
from typing import Any

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)


# ─── Global Error Handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Prevents stack trace leaks in production."""
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    raise exc


# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["Scans"])
app.include_router(api_keys.router, prefix="/api/v1/settings/api-keys", tags=["API Keys"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(ransomlook.router, prefix="/api/v1/ransomlook", tags=["RansomLook"])
app.include_router(cve.router, prefix="/api/v1/cve", tags=["CVE"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["Intelligence"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
