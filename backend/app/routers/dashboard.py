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
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import ViewerUser
from app.models.scan import ScanResult, ScanSeverity, ScanStatus

router = APIRouter()


# ─── /dashboard/stats ─────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def dashboard_stats(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """KPIs affichés dans les 4 cards du haut du dashboard."""
    since_7d = datetime.now(timezone.utc) - timedelta(days=7)

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.started_at >= since_7d)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .order_by(ScanResult.started_at.desc())
    )
    scans = result.scalars().all()

    last_scan = scans[0] if scans else None

    return {
        "scans_7d": len(scans),
        "critical_count": sum(
            1 for s in scans if s.severity == ScanSeverity.CRITICAL
        ),
        "total_findings": sum(s.total_findings for s in scans),
        "last_scan_at": last_scan.completed_at.isoformat() if last_scan and last_scan.completed_at else None,
    }


# ─── /dashboard/chart ─────────────────────────────────────────────────────────

@router.get("/dashboard/chart")
async def dashboard_chart(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    period: str = Query("7d", pattern="^(7d|1m|6m|12m)$"),
) -> list[dict[str, Any]]:
    """
    Données pour le graphique Detection Volume (stacked bar chart).
    Retourne une liste de {date, critical, high, medium, low, total}.
    """
    period_days = {"7d": 7, "1m": 30, "6m": 180, "12m": 365}[period]
    since = datetime.now(timezone.utc) - timedelta(days=period_days)

    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.started_at >= since)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .order_by(ScanResult.started_at.asc())
    )
    scans = result.scalars().all()

    daily: dict[str, dict[str, int]] = defaultdict(
        lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0}
    )

    severity_key = {
        ScanSeverity.CRITICAL: "critical",
        ScanSeverity.HIGH: "high",
        ScanSeverity.MEDIUM: "medium",
        ScanSeverity.LOW: "low",
        ScanSeverity.NONE: "low",  # compté dans low visuellement
    }

    for scan in scans:
        day = scan.started_at.astimezone(timezone.utc).strftime("%b %d")
        daily[day]["total"] += scan.total_findings
        if scan.severity and scan.severity in severity_key:
            daily[day][severity_key[scan.severity]] += scan.total_findings

    return [{"date": d, **v} for d, v in sorted(daily.items())]


# ─── /connectors/status ───────────────────────────────────────────────────────

@router.get("/connectors/status")
async def connectors_status(current_user: ViewerUser) -> list[dict[str, Any]]:
    """
    État de chaque connecteur, dérivé des propriétés *_configured de Settings.
    RansomLook en mode local est toujours considéré actif (service Docker interne).
    RansomLook en mode saas nécessite une clé ET une réponse réussie.
    """
    connectors = [
        {
            "service_name": "hibp",
            "service_label": "HIBP",
            "configured": settings.hibp_configured,
            "is_active": settings.hibp_configured,
            "last_test_success": None,
        },
        {
            "service_name": "leakcheck",
            "service_label": "LeakCheck",
            "configured": settings.leakcheck_configured,
            "is_active": settings.leakcheck_configured,
            "last_test_success": None,
        },
        {
            "service_name": "ransomlook",
            "service_label": "RansomLook",
            # local: actif par défaut (Docker interne). saas: nécessite une clé.
            "configured": (
                settings.ransomlook_mode == "local"
                or bool(settings.ransomlook_saas_api_key)
            ),
            "is_active": (
                settings.ransomlook_mode == "local"
                or bool(settings.ransomlook_saas_api_key)
            ),
            "last_test_success": None,
        },
        {
            "service_name": "github",
            "service_label": "GitHub",
            "configured": settings.github_configured,
            "is_active": settings.github_configured,
            "last_test_success": None,
        },
        {
            "service_name": "urlscan",
            "service_label": "URLScan.io",
            "configured": settings.urlscan_configured,
            "is_active": settings.urlscan_configured,
            "last_test_success": None,
        },
        {
            "service_name": "dehashed",
            "service_label": "Dehashed",
            "configured": settings.dehashed_configured,
            "is_active": settings.dehashed_configured,
            "last_test_success": None,
        },
        {
            "service_name": "intelx",
            "service_label": "IntelX",
            "configured": settings.intelx_configured,
            "is_active": settings.intelx_configured,
            "last_test_success": None,
        },
        {
            "service_name": "otx",
            "service_label": "AlienVault OTX",
            "configured": settings.otx_configured,
            "is_active": settings.otx_configured,
            "last_test_success": None,
        },
        {
            "service_name": "shodan",
            "service_label": "Shodan",
            "configured": settings.shodan_configured,
            "is_active": settings.shodan_configured,
            "last_test_success": None,
        },
        {
            "service_name": "gitlab",
            "service_label": "GitLab",
            "configured": settings.gitlab_configured,
            "is_active": settings.gitlab_configured,
            "last_test_success": None,
        },
    ]

    return connectors


# ─── /findings ────────────────────────────────────────────────────────────────

@router.get("/findings")
async def list_findings(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("discovered_at:desc"),
) -> list[dict[str, Any]]:
    """
    Dernières trouvailles pour la table Latest Findings du dashboard.
    Chaque ScanResult est "explosé" par source via findings_by_source.
    """
    result = await db.execute(
        select(ScanResult)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .where(ScanResult.total_findings > 0)
        .order_by(ScanResult.started_at.desc())
        .limit(limit)
    )
    scans = result.scalars().all()

    rows: list[dict[str, Any]] = []
    for scan in scans:
        if scan.findings_by_source:
            for source, count in scan.findings_by_source.items():
                if count and count > 0:
                    rows.append({
                        "id": f"{scan.id}-{source}",
                        "severity": (scan.severity.value.upper() if scan.severity else "LOW"),
                        "source": source,
                        "domain": scan.target_domain,
                        "type": _source_to_type(source),
                        "count": count,
                        "discovered_at": scan.started_at.isoformat(),
                    })
        else:
            # Pas de détail par source — on expose un row générique
            rows.append({
                "id": str(scan.id),
                "severity": (scan.severity.value.upper() if scan.severity else "LOW"),
                "source": scan.triggered_by or "scheduler",
                "domain": scan.target_domain,
                "type": "Scan",
                "count": scan.total_findings,
                "discovered_at": scan.started_at.isoformat(),
            })

    return rows[:limit]


def _source_to_type(source: str) -> str:
    """Mappe un identifiant source à un type lisible pour la table."""
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
