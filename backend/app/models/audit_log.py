"""
BreachRadar WebUI — AuditLog Template (SQLAlchemy)
===================================================
Traceability of all admin actions (GDPR audit trail).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """
    Audit log — traces all sensitive actions:
    - Connections / disconnections
    - Configuration changes (API keys, SMTP)
    - User management
    - Manual scan triggers
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Who ─────────────────────────────── ────────────────────────────────
    user_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )  # Null for system actions

    # ─── What ─────────────────────────────── ───────────────────────────────
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    # Ex: "auth.login.success", "auth.login.failure", "user.created",
    #     "apikey.updated", "scan.triggered", "smtp.configured"

    # ─── Context ───────────────────────────── ─────────────────────────────
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Ex: {"target_user": "bob@corp.com", "role_changed": "viewer→admin"}
    # ⚠️ NEVER credentials or sensitive data in details

    # ─── IP / Client ─────────────────────────── ────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Timestamp ──────────────────────────── ─────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} user={self.user_email}>"
