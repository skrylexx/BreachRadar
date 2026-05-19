"""
BreachRadar WebUI — Routeur RansomLook
======================================
Proxies et endpoints pour les alertes Ransomware.
"""

from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.dependencies.auth import ViewerUser
from app.clients.ransomlook import RansomLookClient
from app.models.api_key import APIKey
from app.core.security import decrypt_secret
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

async def get_fresh_ransom_client(db: AsyncSession) -> RansomLookClient:
    """Initialise un client RansomLook avec la clé API (priorité DB > .env)."""
    api_key = None
    if settings.ransomlook_mode == "saas" and not settings.ransomlook_saas_api_key:
        result = await db.execute(select(APIKey).where(APIKey.service_name == "ransomlook_saas"))
        key_record = result.scalar_one_or_none()
        if key_record and key_record.is_active:
            try:
                api_key = decrypt_secret(key_record.encrypted_key)
            except Exception:
                pass
    
    return RansomLookClient(api_key=api_key)

class RansomwareAlertRead(BaseModel):
    id: str
    group: str
    victim: str
    status: str
    discovered_at: datetime
    published_at: Optional[datetime] = None
    description: Optional[str] = None
    country: Optional[str] = None
    activity: Optional[str] = None
    claim_size: Optional[str] = None

@router.get("/status")
async def get_ransomlook_status(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db)
):
    """État de l'instance RansomLook."""
    client = await get_fresh_ransom_client(db)
    stats = await client.check_health()
    return stats.model_dump()

@router.get("/alerts", response_model=PaginatedResponse[RansomwareAlertRead])
async def list_ransomware_alerts(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    group: Optional[str] = None,
    domain: Optional[str] = Query(None), # Ajout du filtre domaine
    status: Optional[str] = None,
    period: Optional[str] = None,
):
    """Liste les alertes Ransomware via l'API RansomLook."""
    client = await get_fresh_ransom_client(db)
    
    try:
        # Si un domaine est spécifié, on fait une recherche ciblée
        if domain:
            findings = await client.check_domain(domain)
            filtered = [
                RansomwareAlertRead(
                    id=f"{f.group_name}-{f.victim_name}",
                    group=f.group_name,
                    victim=f.victim_name,
                    status=f.status.value,
                    discovered_at=f.discovered_at,
                    published_at=f.published_at,
                    description=None,
                    country=None,
                    activity=None,
                    claim_size=None,
                ) for f in findings
            ]
        else:
            # Sinon, on récupère les victimes récentes (vue globale)
            days = 30
            if period == "7d": days = 7
            elif period == "1m": days = 30
            elif period == "6m": days = 180
            elif period == "12m": days = 365
            
            raw_victims = await client.get_recent_victims(days=days)
            
            filtered = []
            for v in raw_victims:
                if group and v.get("group_name") != group:
                    continue
                filtered.append(RansomwareAlertRead(
                    id=f"{v.get('group_name')}-{v.get('post_title')}",
                    group=v.get("group_name", "unknown"),
                    victim=v.get("post_title", "unknown"),
                    status="PUBLISHED" if v.get("published") else "LISTED",
                    discovered_at=v.get("discovered") or v.get("added") or datetime.now(),
                    published_at=v.get("published"),
                    description=v.get("description"),
                    country=v.get("country"),
                    activity=v.get("activity"),
                    claim_size=v.get("claim_size"),
                ))
            
        # Pagination manuelle
        total = len(filtered)
        items = filtered[offset : offset + limit]
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=(offset // limit) + 1,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RansomLook API error: {str(e)}")
