"""
BreachRadar WebUI — Modèle SystemSettings (SQLAlchemy)
======================================================
Stockage des paramètres de l'instance modifiables via la WebUI.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemSettings(Base):
    """
    Paramètres globaux du système (TARGET_DOMAIN, maintenance_mode, etc.).
    Utilise une structure Key-Value avec stockage JSON pour la flexibilité.
    """
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<SystemSettings key={self.key} value={self.value}>"
