"""
BreachRadar WebUI — Schémas Finding (Pydantic)
==============================================
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.finding import Severity

# ─── Nouvelles Trouvailles (Veille Numérique) ───────────────────────────────


class CyberFindingRead(BaseModel):
    id: uuid.UUID
    source: str
    external_id: str
    finding_type: str
    title: str
    description: str | None
    url: str | None
    severity: Severity
    extra_metadata: dict | None
    is_read: bool
    discovered_at: datetime
    published_at: datetime | None

    model_config = {"from_attributes": True}


class CyberFindingList(BaseModel):
    items: list[CyberFindingRead]
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
