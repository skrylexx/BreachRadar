"""
BreachRadar WebUI — ScanResult Model (SQLAlchemy)
====================================================
Storage of scan results (without sensitive data — GDPR).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScanStatus(enum.StrEnum):
    """Status of a scan."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanSeverity(enum.StrEnum):
    """Overall severity of a scan (cyber standard color code)."""

    CRITICAL = "critical"  # Red — Positive RansomLook
    HIGH = "high"  # Orange
    MEDIUM = "medium"  # YELLOW
    LOW = "low"  # Blue/Gray
    NONE = "none"  # Green — no findings


class ScanResult(Base):
    """Result of a BreachRadar scan (aggregated data, without credentials)."""

    __tablename__ = "scan_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Scan context ───────────────────────── ─────────────────────────
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

    # ─── Statistics (without sensitive data) ─────────────────────────────
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    ransomware_findings: Mapped[int] = mapped_column(Integer, default=0)
    breach_findings: Mapped[int] = mapped_column(Integer, default=0)

    # ─── Summary by source (aggregated JSON) ──────────────────────────────────
    # Ex: {"hibp": 3, "leakcheck": 1, "ransomlook": 0, "github": 2}
    findings_by_source: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ─── Report (file path, not content) ───────────────────────
    report_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(
        String(64), default="scheduler", nullable=False
    )  # "schedule" | "manual:user@email.com"

    # ─── Timestamps ──────────────────────────── ────────────────────────────
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
