"""
BreachRadar WebUI — Routeur Settings (Admin uniquement)
========================================================
Gestion des paramètres système et des sources custom.
"""

from typing import Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import AdminUser, ViewerUser
from app.models.audit_log import AuditLog
from app.models.cve import CustomFeedSource
from app.models.settings import SystemSettings

router = APIRouter()

# ─── Schémas ──────────────────────────────────────────────────────────────────


class SystemSettingUpdate(BaseModel):
    key: str
    value: str | int | bool | dict[str, Any] | list[Any]


class CustomSourceCreate(BaseModel):
    name: str
    url: str
    category: str = "General"
    enabled: bool = True


class CustomSourceRead(BaseModel):
    id: str
    name: str
    url: str
    category: str
    enabled: bool
    last_item_count: int

    model_config = {"from_attributes": True}


# ─── System Settings ──────────────────────────────────────────────────────────


@router.get("/general")
async def get_general_settings(current_user: AdminUser, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Récupère tous les paramètres système."""
    result = await db.execute(select(SystemSettings))
    settings_list = result.scalars().all()
    return {s.key: s.value for s in settings_list}


@router.put("/general")
async def update_general_setting(
    request: Request,
    body: SystemSettingUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Met à jour un paramètre système."""
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == body.key))
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = body.value
    else:
        setting = SystemSettings(key=body.key, value=body.value)
        db.add(setting)

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="settings.updated",
            details={"key": body.key},
            ip_address=request.client.host if request.client else None,
        )
    )
    return {"status": "ok"}


# ─── Custom Sources ───────────────────────────────────────────────────────────


@router.get("/custom-sources", response_model=list[CustomSourceRead])
async def list_custom_sources(current_user: ViewerUser, db: AsyncSession = Depends(get_db)) -> Sequence[CustomFeedSource]:
    """Liste toutes les sources RSS custom."""
    result = await db.execute(select(CustomFeedSource))
    return result.scalars().all()


@router.post("/custom-sources", response_model=CustomSourceRead)
async def create_custom_source(
    request: Request,
    body: CustomSourceCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> CustomFeedSource:
    """Ajoute une nouvelle source RSS."""
    source = CustomFeedSource(name=body.name, url=body.url, category=body.category, enabled=body.enabled)
    db.add(source)
    await db.flush()

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="custom_source.created",
            details={"name": body.name, "url": body.url},
            ip_address=request.client.host if request.client else None,
        )
    )
    return source


@router.post("/custom-sources/test")
async def test_custom_source(
    body: dict[str, Any],
    current_user: AdminUser,
) -> dict[str, Any]:
    """Teste un flux RSS et renvoie un aperçu des 3 derniers items."""
    import feedparser
    import httpx

    url = body.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code != 200:
                return {"ok": False, "message": f"HTTP {res.status_code}"}

            feed = feedparser.parse(res.text)
            if feed.bozo:
                return {"ok": False, "message": "Invalid XML/RSS structure"}

            preview = []
            for entry in feed.entries[:3]:
                preview.append(
                    {
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link", "#"),
                        "date": entry.get("published", "No date"),
                    }
                )

            return {
                "ok": True,
                "title": feed.feed.get("title", "Unknown Feed"),
                "item_count": len(feed.entries),
                "preview": preview,
            }
    except Exception as e:
        return {"ok": False, "message": str(e)}


@router.delete("/custom-sources/{source_id}")
async def delete_custom_source(
    request: Request, source_id: str, current_user: AdminUser, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Supprime une source RSS."""
    result = await db.execute(select(CustomFeedSource).where(CustomFeedSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    await db.delete(source)
    db.add(
        AuditLog(
            user_email=current_user.email,
            action="custom_source.deleted",
            details={"id": source_id},
            ip_address=request.client.host if request.client else None,
        )
    )
    return {"status": "ok"}
