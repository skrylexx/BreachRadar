"""
BreachRadar WebUI — FastAPI Application Entry Point
====================================================
Point d'entrée principal. Configure le middleware, les routes et le cycle de vie.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import engine, Base
from app import models # Ensure models are registered
from app.core.redis import redis_client
from app.routers import auth, users, scans, api_keys, health, webhooks, ransomlook, cve, settings as settings_router, reports, intelligence
from app.routers.dashboard import router as dashboard_router
from app.core.init_db import initialize_database
from app.engine.scheduler import ScanScheduler

# ─── Rate Limiter global ─────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ─── Cycle de vie (startup / shutdown) ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialisation et nettoyage des ressources."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialiser l'administrateur par défaut si la DB est vide
    await initialize_database()

    # Démarrage du planificateur (Scheduler) en arrière-plan
    scheduler = None
    if getattr(settings, "schedule_enabled", False):
        import logging
        logger = logging.getLogger("breachradar.scheduler")
        logger.info("Démarrage du ScanScheduler en tâche de fond...")
        
        async def _scan_callback():
            """Callback déclenché par le scheduler pour un scan complet."""
            from app.core.database import AsyncSessionLocal
            from app.engine.logic import ScanManager
            from app.models.scan import ScanResult, ScanStatus
            from datetime import datetime, timezone
            
            async with AsyncSessionLocal() as db:
                # 1. Créer l'entrée ScanResult en DB
                scan = ScanResult(
                    target_domain=settings.target_domain,
                    status=ScanStatus.RUNNING,
                    triggered_by="scheduler",
                    started_at=datetime.now(timezone.utc),
                )
                db.add(scan)
                await db.commit()
                await db.refresh(scan)
                
                # 2. Lancer le scan
                scan_manager = ScanManager()
                await scan_manager.run_full_scan(scan.id)

        async def _watch_callback():
            """Callback déclenché par le scheduler pour la veille numérique (CVE + RSS + GitHub)."""
            from app.core.database import AsyncSessionLocal
            from app.engine.cve_monitor import CVEMonitor
            from app.engine.intelligence_monitor import IntelligenceMonitor
            
            # Catégories par défaut à surveiller pour les CVE
            default_categories = ["nvd_windows", "nvd_linux", "osv_pypi", "osv_npm", "osv_go"]
            
            async with AsyncSessionLocal() as db:
                # 1. Veille CVE (NVD, OSV...)
                cve_monitor = CVEMonitor(db)
                # 2. Veille Numérique (RSS, GitHub...)
                intel_monitor = IntelligenceMonitor(db)
                
                try:
                    await asyncio.gather(
                        cve_monitor.poll_all(active_categories=default_categories),
                        intel_monitor.run_all()
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger("breachradar.scheduler")
                    logger.error(f"Erreur lors de la veille programmée : {e}")
                finally:
                    await cve_monitor.close()
                    await intel_monitor.close()
            
        scheduler = ScanScheduler(
            settings=settings, 
            scan_callback=_scan_callback,
            cve_callback=_watch_callback
        )
        scheduler.start()

    yield

    # Shutdown
    if scheduler:
        scheduler.stop()
    await redis_client.aclose()
    await engine.dispose()


# ─── Application FastAPI ──────────────────────────────────────────────────────
app = FastAPI(
    title="BreachRadar WebUI API",
    description="API backend de la WebUI BreachRadar — Gouvernance SOC",
    version="1.0.0",
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────

# Trusted Host — protection contre les Host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts if settings.environment == "production" else ["*"],
)

# CORS — autoriser uniquement les origines configurées
# NOTE: Ajouté APRÈS TrustedHost pour être exécuté AVANT (LIFO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # Requis pour HttpOnly Cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# ─── Gestionnaire d'erreurs global ───────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Évite les fuites de stack traces en production."""
    if settings.environment == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    raise exc


# ─── Routeurs ────────────────────────────────────────────────────────────────
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
