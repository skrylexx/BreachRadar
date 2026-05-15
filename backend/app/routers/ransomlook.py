"""
BreachRadar WebUI — Routeur RansomLook
======================================
Proxies et endpoints pour les alertes Ransomware.
"""

from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from app.dependencies.auth import ViewerUser
from app.clients.ransomlook import RansomLookClient
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

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
async def get_ransomlook_status(current_user: ViewerUser):
    """État de l'instance RansomLook."""
    client = RansomLookClient()
    stats = await client.check_health()
    return stats.model_dump()

@router.get("/alerts", response_model=PaginatedResponse[RansomwareAlertRead])
async def list_ransomware_alerts(
    current_user: ViewerUser,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    group: Optional[str] = None,
    status: Optional[str] = None,
    period: Optional[str] = None,
):
    """Liste les alertes Ransomware via l'API RansomLook."""
    client = RansomLookClient()
    
    # On récupère les victimes récentes (approximation pour la liste globale)
    # Note: L'API RansomLook locale est limitée, on fait au mieux.
    try:
        # On demande plus que le limit pour pouvoir filtrer/paginer si nécessaire
        # Mais l'API /recent est simple.
        days = 30 # Par défaut 30 jours pour la page outil
        if period == "7d": days = 7
        elif period == "1m": days = 30
        elif period == "6m": days = 180
        elif period == "12m": days = 365
        
        raw_victims = await client.get_recent_victims(days=days)
        
        # Filtrage manuel
        filtered = []
        for v in raw_victims:
            if group and v.get("group_name") != group:
                continue
            # status est plus complexe dans RansomLook, on simplifie
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
