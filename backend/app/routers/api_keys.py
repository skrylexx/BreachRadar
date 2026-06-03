"""
BreachRadar WebUI — Routeur API Keys (Admin uniquement)
========================================================
Gestion des clés API des connecteurs OSINT.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import encrypt_secret
from app.dependencies.auth import AdminUser
from app.models.api_key import APIKey
from app.models.audit_log import AuditLog

router = APIRouter()

# Services supportés avec leur description
SUPPORTED_SERVICES = {
    "hibp": "Have I Been Pwned",
    "leakcheck": "LeakCheck.io",
    "dehashed": "Dehashed",
    "intelx": "Intelligence X",
    "github": "GitHub",
    "hunter": "Hunter.io",
    "urlscan": "URLScan.io",
    "otx": "AlienVault OTX",
    "ransomlook_saas": "RansomLook SaaS",
}


class APIKeyCreate(BaseModel):
    service_name: str
    api_key: str


class APIKeyRead(BaseModel):
    service_name: str
    service_label: str
    is_active: bool
    last_test_success: bool | None

    model_config = {"from_attributes": True}


class APIKeyStatus(BaseModel):
    """Vue d'ensemble de tous les connecteurs (configurés ou non)."""

    service_name: str
    service_label: str
    configured: bool
    is_active: bool
    last_test_success: bool | None


@router.get("/status", response_model=list[APIKeyStatus])
async def get_api_keys_status(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> list[APIKeyStatus]:
    """
    Retourne l'état de TOUS les connecteurs supportés.
    Les non-configurés sont inclus avec configured=False.
    """
    result = await db.execute(select(APIKey))
    configured_keys = {k.service_name: k for k in result.scalars().all()}

    statuses = []
    for service, label in SUPPORTED_SERVICES.items():
        key = configured_keys.get(service)
        statuses.append(
            APIKeyStatus(
                service_name=service,
                service_label=label,
                configured=key is not None,
                is_active=key.is_active if key else False,
                last_test_success=key.last_test_success if key else None,
            )
        )

    return statuses


@router.put("/{service_name}")
async def upsert_api_key(
    request: Request,
    service_name: str,
    body: APIKeyCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Crée ou met à jour une clé API (admin uniquement)."""
    if service_name not in SUPPORTED_SERVICES:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service_name}")

    # Stockage de la clé chiffrée via Fernet
    result = await db.execute(select(APIKey).where(APIKey.service_name == service_name))
    existing = result.scalar_one_or_none()

    if existing:
        existing.encrypted_key = encrypt_secret(body.api_key)
        existing.is_active = True
        existing.last_test_success = None
    else:
        key = APIKey(
            service_name=service_name,
            encrypted_key=encrypt_secret(body.api_key),
        )
        db.add(key)

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="apikey.updated",
            details={"service": service_name},
            ip_address=request.client.host if request.client else None,
        )
    )

    return {"message": f"API key for {service_name} saved successfully"}


@router.delete("/{service_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    request: Request,
    service_name: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Supprime une clé API."""
    result = await db.execute(select(APIKey).where(APIKey.service_name == service_name))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")

    await db.delete(key)
    db.add(
        AuditLog(
            user_email=current_user.email,
            action="apikey.deleted",
            details={"service": service_name},
            ip_address=request.client.host if request.client else None,
        )
    )
