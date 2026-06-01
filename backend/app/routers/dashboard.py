"""
BreachRadar WebUI — Routeur Dashboard
======================================
Endpoints consommés par le frontend Server Component (page.tsx) :
  GET /api/v1/dashboard/stats        — KPIs résumés
  GET /api/v1/dashboard/chart        — données graphique Detection Volume
  GET /api/v1/connectors/status      — état des connecteurs selon .env
  GET /api/v1/findings               — dernières trouvailles (table Latest Findings)
"""

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import ViewerUser
from app.models.scan import ScanResult, ScanSeverity, ScanStatus
from app.models.settings import SystemSettings
from app.schemas.common import PaginatedResponse
from app.schemas.finding import FindingRead

router = APIRouter()

# ─── Helpers ──────────────────────────────────────────────────────────────────


async def _get_mock_data_enabled(db: AsyncSession) -> bool:
    """Vérifie si l'affichage des données de démonstration est activé."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == "mock_data_enabled")
    )
    setting = result.scalar_one_or_none()
    return setting.value if setting else False


async def _ransomlook_active(db: AsyncSession) -> bool:
    """Vérifie si RansomLook est réellement joignable."""
    from app.clients.ransomlook import RansomLookClient
    from app.models.api_key import APIKey

    mode = settings.ransomlook_mode

    # 1. SaaS Mode: check for key in .env or DB
    if mode == "saas":
        if settings.ransomlook_saas_api_key:
            return True

        # Check database
        result = await db.execute(select(APIKey).where(APIKey.service_name == "ransomlook_saas"))
        key = result.scalar_one_or_none()
        return key is not None and key.is_active

    # 2. Local Mode: real connectivity test
    try:
        # We use a default client that uses settings
        client = RansomLookClient()
        stats = await client.check_health()
        return stats.is_healthy
    except Exception:
        return False


def _source_to_type(source: str) -> str:
    mapping = {
        "hibp": "Breach",
        "leakcheck": "Breach",
        "dehashed": "Breach",
        "intelx": "Breach",
        "ransomlook": "Ransomware",
        "github": "Github",
        "gitlab": "GitLab",
        "urlscan": "Phishing",
        "otx": "Threat Intel",
        "shodan": "Exposure",
        "telegram": "Telegram",
    }
    return mapping.get(source.lower(), "Other")


# ─── /dashboard/stats ─────────────────────────────────────────────────────────


@router.get("/dashboard/stats")
async def dashboard_stats(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """KPIs affichés dans les 4 cards du haut du dashboard."""
    since_7d = datetime.now(UTC) - timedelta(days=7)

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.started_at >= since_7d)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .order_by(ScanResult.started_at.desc())
    )
    scans = result.scalars().all()

    if not scans and await _get_mock_data_enabled(db):
        return {
            "scans_7d": 12,
            "critical_count": 2,
            "total_findings": 145,
            "last_scan_at": (datetime.now(UTC) - timedelta(hours=4)).isoformat(),
            "is_mock": True,
        }

    last_scan = scans[0] if scans else None

    return {
        "scans_7d": len(scans),
        "critical_count": sum(1 for s in scans if s.severity == ScanSeverity.CRITICAL),
        "total_findings": sum(s.total_findings for s in scans),
        "last_scan_at": (
            last_scan.completed_at.isoformat() if last_scan and last_scan.completed_at else None
        ),
    }


# ─── /dashboard/chart ─────────────────────────────────────────────────────────


@router.get("/dashboard/chart")
async def dashboard_chart(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    period: str = Query("7d", pattern="^(7d|1m|6m|12m)$"),
    source: str | None = None,
) -> list[dict[str, Any]]:
    """
    Données pour le graphique Detection Volume (stacked bar chart).
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

    if not scans and await _get_mock_data_enabled(db):
        return _get_mock_chart_data(period_days)

    daily: dict[str, dict[str, int]] = defaultdict(
        lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}
    )

    severity_key = {
        ScanSeverity.CRITICAL: "critical",
        ScanSeverity.HIGH: "high",
        ScanSeverity.MEDIUM: "medium",
        ScanSeverity.LOW: "low",
        ScanSeverity.NONE: "low",
    }

    for scan in scans:
        day = scan.started_at.astimezone(UTC).strftime("%b %d")
        daily[day]["total"] += scan.total_findings
        if scan.severity and scan.severity in severity_key:
            daily[day][severity_key[scan.severity]] += scan.total_findings

    return [{"date": d, **v} for d, v in sorted(daily.items())]


def _get_mock_chart_data(days: int) -> list[dict[str, Any]]:
    now = datetime.now(UTC)
    data = []
    for i in range(days, -1, -1):
        date = now - timedelta(days=i)
        data.append(
            {
                "date": date.strftime("%b %d"),
                "critical": (i % 3),
                "high": (i % 5),
                "medium": (i % 7),
                "low": (i % 4),
                "total": (i % 3) + (i % 5) + (i % 7) + (i % 4),
            }
        )
    return data


# ─── /connectors/status ───────────────────────────────────────────────────────


@router.get("/connectors/status")
async def connectors_status(
    current_user: ViewerUser, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    """
    État de TOUS les connecteurs disponibles dans l'application.
    Ajoute un flag 'is_mock' si le connecteur n'est pas configuré mais que le mode mock est activé.
    """
    ransomlook_ok = await _ransomlook_active(db)
    mock_enabled = await _get_mock_data_enabled(db)

    def _get_status(configured: bool):
        if configured:
            return "ok"
        return "mock" if mock_enabled else "error"

    return [
        {
            "name": "ransomlook",
            "label": "RansomLook",
            "configured": ransomlook_ok,
            "is_active": ransomlook_ok or mock_enabled,
            "is_mock": not ransomlook_ok and mock_enabled,
            "status": _get_status(ransomlook_ok),
            "last_test_success": True
            if settings.ransomlook_mode == "local"
            else (True if ransomlook_ok else None),
        },
        {
            "name": "hibp",
            "label": "HIBP",
            "configured": settings.hibp_configured,
            "is_active": settings.hibp_configured or mock_enabled,
            "is_mock": not settings.hibp_configured and mock_enabled,
            "status": _get_status(settings.hibp_configured),
            "last_test_success": True if settings.hibp_configured else None,
        },
        {
            "name": "leakcheck",
            "label": "LeakCheck",
            "configured": settings.leakcheck_configured,
            "is_active": settings.leakcheck_configured or mock_enabled,
            "is_mock": not settings.leakcheck_configured and mock_enabled,
            "status": _get_status(settings.leakcheck_configured),
            "last_test_success": True if settings.leakcheck_configured else None,
        },
        {
            "name": "github",
            "label": "GitHub",
            "configured": settings.github_configured,
            "is_active": settings.github_configured or mock_enabled,
            "is_mock": not settings.github_configured and mock_enabled,
            "status": _get_status(settings.github_configured),
            "last_test_success": True if settings.github_configured else None,
        },
        {
            "name": "urlscan",
            "label": "URLScan.io",
            "configured": settings.urlscan_configured,
            "is_active": settings.urlscan_configured or mock_enabled,
            "is_mock": not settings.urlscan_configured and mock_enabled,
            "status": _get_status(settings.urlscan_configured),
            "last_test_success": True if settings.urlscan_configured else None,
        },
        {
            "name": "dehashed",
            "label": "Dehashed",
            "configured": settings.dehashed_configured,
            "is_active": settings.dehashed_configured or mock_enabled,
            "is_mock": not settings.dehashed_configured and mock_enabled,
            "status": _get_status(settings.dehashed_configured),
            "last_test_success": True if settings.dehashed_configured else None,
        },
        {
            "name": "intelx",
            "label": "IntelX",
            "configured": settings.intelx_configured,
            "is_active": settings.intelx_configured or mock_enabled,
            "is_mock": not settings.intelx_configured and mock_enabled,
            "status": _get_status(settings.intelx_configured),
            "last_test_success": True if settings.intelx_configured else None,
        },
        {
            "name": "otx",
            "label": "AlienVault OTX",
            "configured": settings.otx_configured,
            "is_active": settings.otx_configured or mock_enabled,
            "is_mock": not settings.otx_configured and mock_enabled,
            "status": _get_status(settings.otx_configured),
            "last_test_success": True if settings.otx_configured else None,
        },
        {
            "name": "shodan",
            "label": "Shodan",
            "configured": settings.shodan_configured,
            "is_active": settings.shodan_configured or mock_enabled,
            "is_mock": not settings.shodan_configured and mock_enabled,
            "status": _get_status(settings.shodan_configured),
            "last_test_success": True if settings.shodan_configured else None,
        },
        {
            "name": "gitlab",
            "label": "GitLab",
            "configured": settings.gitlab_configured,
            "is_active": settings.gitlab_configured or mock_enabled,
            "is_mock": not settings.gitlab_configured and mock_enabled,
            "status": _get_status(settings.gitlab_configured),
            "last_test_success": True if settings.gitlab_configured else None,
        },
    ]


# ─── /findings ────────────────────────────────────────────────────────────────


@router.get("/findings", response_model=PaginatedResponse[FindingRead])
async def list_findings(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("discovered_at:desc"),
    source: str | None = None,
    period: str | None = None,
) -> PaginatedResponse[FindingRead]:
    """
    Dernières trouvailles pour la table Latest Findings du dashboard.
    Génère des données mockées si configuré et pas de données réelles.
    """
    # 1. Vérification données réelles
    count_query = (
        select(func.count(ScanResult.id))
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .where(ScanResult.total_findings > 0)
    )
    total_result = await db.execute(count_query)
    total_scans = total_result.scalar_one()

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .where(ScanResult.total_findings > 0)
        .order_by(ScanResult.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    scans = result.scalars().all()

    rows: list[FindingRead] = []

    for scan in scans:
        if scan.findings_by_source:
            for src, count in scan.findings_by_source.items():
                if source and src.lower() != source.lower():
                    continue
                if count and count > 0:
                    rows.append(
                        FindingRead(
                            id=f"{scan.id}-{src}",
                            severity=(scan.severity.value.upper() if scan.severity else "LOW"),
                            source=src,
                            domain=scan.target_domain,
                            type=_source_to_type(src),
                            count=count,
                            discovered_at=scan.started_at,
                        )
                    )
        else:
            if not source:
                rows.append(
                    FindingRead(
                        id=str(scan.id),
                        severity=(scan.severity.value.upper() if scan.severity else "LOW"),
                        source=scan.triggered_by or "scheduler",
                        domain=scan.target_domain,
                        type="Scan",
                        count=scan.total_findings,
                        discovered_at=scan.started_at,
                    )
                )

    # 2. Si aucune donnée et mock activé
    if not rows and await _get_mock_data_enabled(db):
        return _get_mock_findings(source, limit, offset)

    return PaginatedResponse(
        items=rows, total=total_scans, page=(offset // limit) + 1, page_size=limit
    )


def _get_mock_findings(
    source: str | None, limit: int, offset: int
) -> PaginatedResponse[FindingRead]:
    """Génère des données factices réalistes."""
    sources = [source] if source else ["hibp", "leakcheck", "github", "ransomlook", "urlscan"]
    mock_items = []

    for i in range(limit):
        src = sources[i % len(sources)]
        mock_items.append(
            FindingRead(
                id=f"mock-{offset + i}",
                severity="HIGH" if i % 3 == 0 else "MEDIUM" if i % 2 == 0 else "LOW",
                source=src,
                domain="example-demo.com",
                type=_source_to_type(src),
                count=(i + 1) * 10,
                discovered_at=datetime.now(UTC) - timedelta(hours=i * 2),
            )
        )

    return PaginatedResponse(
        items=mock_items,
        total=100,  # Mock total
        page=(offset // limit) + 1,
        page_size=limit,
    )
