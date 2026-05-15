from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import ViewerUser, AdminUser
from app.schemas.cve import CVEAlert, CVESeverity, CVESource, CVESettings, CVESourceStatus
from app.schemas.common import PaginatedResponse

router = APIRouter()

# Données de test (Mocks)
MOCK_CVE_ALERTS = [
    CVEAlert(
        id="CVE-2024-1234",
        cve_id="CVE-2024-1234",
        title="Critical RCE in Windows Kernel",
        description="A remote code execution vulnerability exists in the Windows Kernel when it fails to properly handle certain objects in memory.",
        severity=CVESeverity.CRITICAL,
        cvss_score=9.8,
        category="Windows",
        source=CVESource.NVD,
        url="https://nvd.nist.gov/vuln/detail/CVE-2024-1234",
        published_at=datetime.now(timezone.utc) - timedelta(hours=2)
    ),
    CVEAlert(
        id="CVE-2024-5678",
        cve_id="CVE-2024-5678",
        title="Path Traversal in npm package 'example'",
        description="The 'example' package before version 1.2.3 is vulnerable to path traversal via the 'file' parameter.",
        severity=CVESeverity.HIGH,
        cvss_score=7.5,
        category="Open Source (npm)",
        source=CVESource.OSV,
        url="https://osv.dev/vulnerability/CVE-2024-5678",
        published_at=datetime.now(timezone.utc) - timedelta(days=1)
    ),
    CVEAlert(
        id="CVE-2023-9999",
        cve_id="CVE-2023-9999",
        title="Denial of Service in Linux Kernel",
        description="A denial of service vulnerability was found in the Linux Kernel's networking stack.",
        severity=CVESeverity.MEDIUM,
        cvss_score=5.5,
        category="Linux Kernel",
        source=CVESource.NVD,
        url="https://nvd.nist.gov/vuln/detail/CVE-2023-9999",
        published_at=datetime.now(timezone.utc) - timedelta(days=5)
    ),
]

@router.get("/alerts", response_model=PaginatedResponse[CVEAlert])
async def get_cve_alerts(
    current_user: ViewerUser,
    severity: Optional[List[CVESeverity]] = Query(None),
    category: Optional[List[str]] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[CVEAlert]:
    """Retourne la liste agrégée des CVE récentes selon les catégories actives."""
    filtered = MOCK_CVE_ALERTS
    
    if severity:
        filtered = [a for a in filtered if a.severity in severity]
    if category:
        filtered = [a for a in filtered if a.category in category]
        
    total = len(filtered)
    items = filtered[offset : offset + limit]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=(offset // limit) + 1,
        page_size=limit
    )

@router.get("/settings", response_model=CVESettings)
async def get_cve_settings(current_user: ViewerUser) -> CVESettings:
    """Retourne les catégories actives sauvegardées."""
    return CVESettings(
        active_categories=["Windows", "Linux Kernel", "Open Source (npm)", "Critical CVEs"],
        polling_interval_minutes=60,
        include_no_cvss=False
    )

@router.put("/settings")
async def update_cve_settings(settings: CVESettings, current_user: AdminUser) -> dict:
    """Sauvegarde les catégories sélectionnées par l'admin."""
    return {"status": "ok", "message": "Settings updated"}

@router.get("/status", response_model=List[CVESourceStatus])
async def get_cve_status(current_user: ViewerUser) -> List[CVESourceStatus]:
    # ... (unchanged)

@router.get("/trend")
async def get_cve_trend(
    current_user: ViewerUser,
    period: str = Query("7d", pattern="^(7d|1m|6m|12m)$"),
) -> List[dict]:
    """Données pour le graphique d'évolution des CVE."""
    days = {"7d": 7, "1m": 30, "6m": 180, "12m": 365}[period]
    now = datetime.now(timezone.utc)
    
    data = []
    for i in range(days, -1, -1):
        date = now - timedelta(days=i)
        data.append({
            "date": date.strftime("%b %d"),
            "critical": (i % 3),
            "high": (i % 5),
            "medium": (i % 7),
            "low": (i % 4),
            "total": (i % 3) + (i % 5) + (i % 7) + (i % 4)
        })
    return data
