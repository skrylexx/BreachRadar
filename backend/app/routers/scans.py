"""
BreachRadar WebUI — Scans Router
====================================
Endpoints: list, details, stats, manual trigger, report export.
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import AdminUser, ViewerUser
from app.models.scan import ScanResult, ScanSeverity, ScanStatus
from app.schemas.common import PaginatedResponse
from app.schemas.scan import ScanResultRead, ScanStats, ScanTriggerRequest, ScanTriggerResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=PaginatedResponse[ScanResultRead])
async def list_scans(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = Query(25, ge=1, le=100),
    severity: ScanSeverity | None = None,
) -> PaginatedResponse[ScanResultRead]:
    """Lists scan results (Viewer + Admin)."""
    offset = (page - 1) * page_size

    # Count total
    count_query = select(func.count(ScanResult.id))
    if severity:
        count_query = count_query.where(ScanResult.severity == severity)
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = select(ScanResult).order_by(ScanResult.started_at.desc())

    if severity:
        query = query.where(ScanResult.severity == severity)

    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    scans = result.scalars().all()

    return PaginatedResponse(
        items=[ScanResultRead.model_validate(s) for s in scans],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=ScanStats)
async def get_scan_stats(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    period: str = Query("7d", pattern="^(7d|1m|6m|12m)$"),
) -> ScanStats:
    """
    Aggregated statistics for dashboard charts.
    Returns data points for the bar chart.
    """
    period_days = {"7d": 7, "1m": 30, "6m": 180, "12m": 365}[period]
    since = datetime.now(UTC) - timedelta(days=period_days)

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.started_at >= since)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .order_by(ScanResult.started_at.asc())
    )
    scans = result.scalars().all()

    # Group by day
    from collections import defaultdict

    daily: dict = defaultdict(lambda: {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0})
    for scan in scans:
        day = scan.started_at.date().isoformat()
        daily[day]["total"] += scan.total_findings
        if scan.severity:
            daily[day][scan.severity.value] += 1

    return ScanStats(
        period=period,
        data_points=[{"date": d, **v} for d, v in sorted(daily.items())],
        summary={
            "total_scans": len(scans),
            "total_findings": sum(s.total_findings for s in scans),
            "critical_count": sum(1 for s in scans if s.severity == ScanSeverity.CRITICAL),
        },
    )


@router.get("/{scan_id}", response_model=ScanResultRead)
async def get_scan(
    scan_id: str,
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
) -> ScanResultRead:
    """Details of a scan."""
    import uuid

    result = await db.execute(select(ScanResult).where(ScanResult.id == uuid.UUID(scan_id)))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanResultRead.model_validate(scan)


@router.post("/trigger", response_model=ScanTriggerResponse, status_code=201)
@limiter.limit(settings.rate_limit_scan_trigger)
async def trigger_scan(
    request: Request,
    body: ScanTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: AdminUser,  # Admin only
    db: AsyncSession = Depends(get_db),
) -> ScanTriggerResponse:
    """
    Triggers a manual scan (Admin only).
    """
    started_at = datetime.now(UTC)
    scan = ScanResult(
        target_domain=body.target_domain or settings.target_domain,
        status=ScanStatus.RUNNING,
        triggered_by=f"manual:{current_user.email}",
        started_at=started_at,
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Trigger the scan in the background
    from app.engine.logic import ScanManager

    scan_manager = ScanManager()
    background_tasks.add_task(scan_manager.run_full_scan, scan.id, body.target_domain)

    return ScanTriggerResponse(scan_id=scan.id, started_at=started_at)
