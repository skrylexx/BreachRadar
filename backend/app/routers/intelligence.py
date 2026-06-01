"""
BreachRadar WebUI — Routeur Intelligence
=========================================
Endpoints pour la veille numérique (RSS, GitHub, etc.).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import ViewerUser
from app.models.finding import CyberFinding, Severity
from app.schemas.finding import CyberFindingList

router = APIRouter()


@router.get("", response_model=CyberFindingList)
async def list_intelligence_findings(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    finding_type: str | None = None,
    severity: Severity | None = None,
    source: str | None = None,
    is_read: bool | None = None,
):
    """
    Liste les trouvailles de la veille numérique avec pagination et filtres.
    """
    stmt = select(CyberFinding)

    if finding_type:
        stmt = stmt.where(CyberFinding.finding_type == finding_type)
    if severity:
        stmt = stmt.where(CyberFinding.severity == severity)
    if source:
        stmt = stmt.where(CyberFinding.source == source)
    if is_read is not None:
        stmt = stmt.where(CyberFinding.is_read == is_read)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Sort and paginate
    stmt = stmt.order_by(desc(CyberFinding.published_at), desc(CyberFinding.discovered_at))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    items = result.scalars().all()

    return {"items": items, "total": total or 0, "page": page, "page_size": page_size}


@router.post("/{finding_id}/read")
async def mark_as_read(
    finding_id: str, current_user: ViewerUser, db: AsyncSession = Depends(get_db)
):
    """Marque une trouvaille comme lue."""
    result = await db.execute(select(CyberFinding).where(CyberFinding.id == finding_id))
    item = result.scalar_one_or_none()
    if item:
        item.is_read = True
        await db.commit()
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_as_read(current_user: ViewerUser, db: AsyncSession = Depends(get_db)):
    """Marque toutes les trouvailles comme lues."""
    from sqlalchemy import update

    await db.execute(update(CyberFinding).where(CyberFinding.is_read.is_(False)).values(is_read=True))
    await db.commit()
    return {"status": "ok"}
