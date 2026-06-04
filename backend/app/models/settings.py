"""
BreachRadar WebUI — SystemSettings template (SQLAlchemy)
============================================================
Storage of instance parameters modifiable via the WebUI.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemSettings(Base):
    """
    Global system settings (TARGET_DOMAIN, maintenance_mode, etc.).
    Uses a Key-Value structure with JSON storage for flexibility.
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
