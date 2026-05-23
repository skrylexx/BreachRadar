"""
BreachRadar WebUI — Schémas Finding (Pydantic)
==============================================
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.finding import Severity

# ─── Nouvelles Trouvailles (Veille Numérique) ───────────────────────────────

class CyberFindingRead(BaseModel):
    id: uuid.UUID
    source: str
    external_id: str
    finding_type: str
    title: str
    description: Optional[str]
    url: Optional[str]
    severity: Severity
    extra_metadata: Optional[dict]
    is_read: bool
    discovered_at: datetime
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}

class CyberFindingList(BaseModel):
    items: List[CyberFindingRead]
    total: int
    page: int
    page_size: int

# ─── Anciennes Trouvailles (Dashboard / Scans) ──────────────────────────────

class FindingRead(BaseModel):
    """Résumé d'une trouvaille pour le tableau du dashboard."""
    id: str
    severity: str
    source: str
    domain: str
    type: str
    count: int
    discovered_at: datetime

    model_config = {"from_attributes": True}
