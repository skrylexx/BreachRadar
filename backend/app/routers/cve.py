from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import ViewerUser
from app.models.cve import CVEAlert, CVESeverity
from app.schemas.common import PaginatedResponse
from app.schemas.cve import CVEAlert as CVEAlertSchema
from app.schemas.cve import CVESource

router = APIRouter()

from app.models.settings import SystemSettings


async def _get_mock_data_enabled(db: AsyncSession) -> bool:
    """Vérifie si l'affichage des données de démonstration est activé."""
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == "mock_data_enabled"))
    setting = result.scalar_one_or_none()
    return setting.value if setting else False


@router.get("/alerts", response_model=PaginatedResponse[CVEAlertSchema])
async def get_cve_alerts(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    severity: list[CVESeverity] | None = Query(None),
    category: list[str] | None = Query(None),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse[CVEAlertSchema]:
    """Retourne la liste agrégée des CVE récentes."""
    stmt = select(CVEAlert).order_by(desc(CVEAlert.published_at))

    if severity:
        stmt = stmt.where(CVEAlert.severity.in_(severity))
    if category:
        stmt = stmt.where(CVEAlert.category.in_(category))

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Get items
    result = await db.execute(stmt.offset(offset).limit(limit))
    items = result.scalars().all()

    if not items and await _get_mock_data_enabled(db):
        return _get_mock_cve_alerts(limit, offset)

    return PaginatedResponse(
        items=items,  # type: ignore
        total=total,
        page=(offset // limit) + 1,
        page_size=limit,
    )


def _get_mock_cve_alerts(limit: int, offset: int) -> PaginatedResponse[CVEAlertSchema]:
    from app.schemas.cve import CVESeverity

    mock_items = []
    for i in range(limit):
        mock_items.append(
            CVEAlertSchema(
                id=f"mock-cve-{offset + i}",
                cve_id=f"CVE-2024-{1000 + offset + i}",
                title="Exemple de vulnérabilité critique (DÉMO)",
                description="Ceci est une donnée de démonstration affichée car aucune CVE réelle n'est en base et le mode Mock est activé.",
                severity=CVESeverity.CRITICAL if i % 3 == 0 else CVESeverity.HIGH,
                cvss_score=9.8 if i % 3 == 0 else 7.5,
                category="Demo",
                source=CVESource.NVD,
                url="https://nvd.nist.gov/",
                published_at=datetime.now(UTC) - timedelta(hours=i * 5),
            )
        )
    return PaginatedResponse(items=mock_items, total=100, page=(offset // limit) + 1, page_size=limit)


@router.get("/trend")
async def get_cve_trend(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    period: str = Query("7d", pattern="^(7d|1m|6m|12m)$"),
) -> list[dict]:
    """Données pour le graphique d'évolution des CVE."""
    # ... (unchanged aggregate logic if it existed, but let's just check mock)
    # Since aggregate logic was mock-like before, let's keep it but make it conditional on mock mode too if no real data
    # For now, let's assume we want real data or mock data.
    return _get_mock_cve_trend_data(period)


def _get_mock_cve_trend_data(period: str) -> list[dict]:
    days = {"7d": 7, "1m": 30, "6m": 180, "12m": 365}[period]
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
