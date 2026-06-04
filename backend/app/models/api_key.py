"""
BreachRadar WebUI — APIKey Model (SQLAlchemy)
==============================================================
Encrypted storage of OSINT connectors API keys.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class APIKey(Base):
    """API key of a connector (HIBP, LeakCheck, Dehashed, IntelX...)."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Connector identity ────────────────────── ──────────────────────
    service_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )  # Ex: "hibp", "leakcheck", "dehashed", "intelx", "github"

    # ─── Encrypted key ────────────────────────── ───────────────────────────
    # The key is stored encrypted (Fernet) — never in the clear
    encrypted_key: Mapped[str] = mapped_column(String(1024), nullable=False)

    # ─── Status ────────────────────────────── ──────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_test_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ─── Metadata ─────────────────────────── ────────────────────────────
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<APIKey service={self.service_name} active={self.is_active}>"
