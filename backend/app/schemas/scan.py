"""
BreachRadar WebUI — Schémas Scan (Pydantic)
==========================================
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.scan import ScanSeverity, ScanStatus


class ScanResultRead(BaseModel):
    """Résultat de scan exposé via l'API."""

    id: uuid.UUID
    target_domain: str
    status: ScanStatus
    severity: ScanSeverity | None
    total_findings: int
    ransomware_findings: int
    breach_findings: int
    findings_by_source: dict[str, int] | None
    triggered_by: str
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ScanStats(BaseModel):
    """Statistiques agrégées pour les graphiques du dashboard."""

    # Données pour le graphique à bâtonnets (7j, 1 mois, 6 mois, 12 mois)
    period: str  # "7d" | "1m" | "6m" | "12m"
    data_points: list[dict]  # [{"date": "2026-01-15", "total": 12, "critical": 2, ...}]
    summary: dict  # Totaux sur la période

    model_config = {"from_attributes": True}


class ScanTriggerRequest(BaseModel):
    """Déclenchement manuel d'un scan (admin uniquement)."""

    target_domain: str | None = None  # Si None, utilise le domaine configuré

    @field_validator("target_domain")
    @classmethod
    def validate_domain(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Validation simple de domaine pour éviter SSRF et injections
        # Doit contenir au moins un point, pas d'espaces, pas de caractères spéciaux louches
        if not re.match(r"^[a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid target domain format")
        if v:
            # Interdire localhost et IPs locales pour prévenir SSRF
            blacklist = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]  # nosec B104
            if v.lower() in blacklist:
                raise ValueError("Target domain cannot be a local address")
        return v


class ScanTriggerResponse(BaseModel):
    """Réponse au déclenchement d'un scan."""

    scan_id: uuid.UUID
    message: str = "Scan triggered successfully"
    started_at: datetime
