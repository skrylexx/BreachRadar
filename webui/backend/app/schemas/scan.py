"""
BreachRadar WebUI — Schémas Scan (Pydantic)
==========================================
"""

import uuid
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from app.models.scan import ScanSeverity, ScanStatus


class ScanResultRead(BaseModel):
    """Résultat de scan exposé via l'API."""
    id: uuid.UUID
    target_domain: str
    status: ScanStatus
    severity: Optional[ScanSeverity]
    total_findings: int
    ransomware_findings: int
    breach_findings: int
    findings_by_source: Optional[Dict[str, int]]
    triggered_by: str
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ScanStats(BaseModel):
    """Statistiques agrégées pour les graphiques du dashboard."""
    # Données pour le graphique à bâtonnets (7j, 1 mois, 6 mois, 12 mois)
    period: str  # "7d" | "1m" | "6m" | "12m"
    data_points: list[dict]  # [{"date": "2026-01-15", "total": 12, "critical": 2, ...}]
    summary: dict             # Totaux sur la période

    model_config = {"from_attributes": True}


class ScanTriggerRequest(BaseModel):
    """Déclenchement manuel d'un scan (admin uniquement)."""
    target_domain: Optional[str] = None  # Si None, utilise le domaine configuré


class ScanTriggerResponse(BaseModel):
    """Réponse au déclenchement d'un scan."""
    scan_id: uuid.UUID
    message: str = "Scan triggered successfully"
    started_at: datetime
