"""
BreachRadar WebUI — Routeur Settings (Admin uniquement)
========================================================
Gestion des paramètres système et des sources custom.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import AdminUser, ViewerUser
from app.models.settings import SystemSettings
from app.models.cve import CustomFeedSource
from app.models.audit_log import AuditLog

router = APIRouter()

# ─── Schémas ──────────────────────────────────────────────────────────────────

class SystemSettingUpdate(BaseModel):
    key: str
    value: str | int | bool | dict | list

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
async def get_general_settings(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Récupère tous les paramètres système."""
    result = await db.execute(select(SystemSettings))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}

@router.put("/general")
async def update_general_setting(
    request: Request,
    body: SystemSettingUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Met à jour un paramètre système."""
    result = await db.execute(select(SystemSettings).where(SystemSettings.key == body.key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = body.value
    else:
        setting = SystemSettings(key=body.key, value=body.value)
        db.add(setting)
        
    db.add(AuditLog(
        user_email=current_user.email,
        action="settings.updated",
        details={"key": body.key},
        ip_address=request.client.host if request.client else None
    ))
    return {"status": "ok"}

# ─── Custom Sources ───────────────────────────────────────────────────────────

@router.get("/custom-sources", response_model=List[CustomSourceRead])
async def list_custom_sources(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db)
):
    """Liste toutes les sources RSS custom."""
    result = await db.execute(select(CustomFeedSource))
    return result.scalars().all()

@router.post("/custom-sources", response_model=CustomSourceRead)
async def create_custom_source(
    request: Request,
    body: CustomSourceCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Ajoute une nouvelle source RSS."""
    source = CustomFeedSource(
        name=body.name,
        url=body.url,
        category=body.category,
        enabled=body.enabled
    )
    db.add(source)
    await db.flush()
    
    db.add(AuditLog(
        user_email=current_user.email,
        action="custom_source.created",
        details={"name": body.name, "url": body.url},
        ip_address=request.client.host if request.client else None
    ))
    return source

@router.delete("/custom-sources/{source_id}")
async def delete_custom_source(
    request: Request,
    source_id: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Supprime une source RSS."""
    result = await db.execute(select(CustomFeedSource).where(CustomFeedSource.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    await db.delete(source)
    db.add(AuditLog(
        user_email=current_user.email,
        action="custom_source.deleted",
        details={"id": source_id},
        ip_address=request.client.host if request.client else None
    ))
    return {"status": "ok"}
