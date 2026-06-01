"""
BreachRadar WebUI — Modèles CVE & Sources Custom (SQLAlchemy)
=============================================================
Stockage des alertes de vulnérabilités et des flux RSS personnalisés.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CVESeverity(enum.StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class CVESourceType(enum.StrEnum):
    NVD = "NVD"
    OSV = "OSV"
    GITHUB = "GitHub"
    CVEFEED = "CVEFeed"
    CUSTOM = "Custom"


class CVEAlert(Base):
    """
    Cache des alertes CVE récupérées depuis les sources externes.
    Permet d'afficher les alertes sans interroger les API tierces à chaque requête.
    """

    __tablename__ = "cve_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    cve_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[CVESeverity] = mapped_column(
        Enum(CVESeverity), nullable=False, default=CVESeverity.UNKNOWN
    )
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[CVESourceType] = mapped_column(Enum(CVESourceType), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)

    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CustomFeedSource(Base):
    """
    Sources RSS/Atom personnalisées ajoutées par l'administrateur.
    """

    __tablename__ = "custom_feed_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="General")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_item_count: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
