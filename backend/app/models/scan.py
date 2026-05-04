"""
BreachRadar WebUI — Modèle ScanResult (SQLAlchemy)
===================================================
Stockage des résultats de scan (sans données sensibles — RGPD).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScanStatus(str, enum.Enum):
    """Statut d'un scan."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanSeverity(str, enum.Enum):
    """Sévérité globale d'un scan (code couleur cyber standard)."""
    CRITICAL = "critical"  # Rouge — RansomLook positif
    HIGH = "high"          # Orange
    MEDIUM = "medium"      # Jaune
    LOW = "low"            # Bleu/Gris
    NONE = "none"          # Vert — aucune trouvaille


class ScanResult(Base):
    """Résultat d'un scan BreachRadar (données agrégées, sans credentials)."""

    __tablename__ = "scan_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Contexte du scan ──────────────────────────────────────────────────
    target_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus),
        nullable=False,
        default=ScanStatus.RUNNING,
    )
    severity: Mapped[ScanSeverity] = mapped_column(
        Enum(ScanSeverity),
        nullable=True,
    )

    # ─── Statistiques (sans données sensibles) ─────────────────────────────
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    ransomware_findings: Mapped[int] = mapped_column(Integer, default=0)
    breach_findings: Mapped[int] = mapped_column(Integer, default=0)

    # ─── Résumé par source (JSON agrégé) ──────────────────────────────────
    # Ex: {"hibp": 3, "leakcheck": 1, "ransomlook": 0, "github": 2}
    findings_by_source: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ─── Rapport (chemin du fichier, pas le contenu) ───────────────────────
    report_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(
        String(64), default="scheduler", nullable=False
    )  # "scheduler" | "manual:user@email.com"

    # ─── Timestamps ────────────────────────────────────────────────────────
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ScanResult id={self.id} domain={self.target_domain} severity={self.severity}>"
