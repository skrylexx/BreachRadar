"""
BreachRadar WebUI — Modèle AuditLog (SQLAlchemy)
=================================================
Traçabilité de toutes les actions admin (audit trail RGPD).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """
    Journal d'audit — trace toutes les actions sensibles :
    - Connexions / déconnexions
    - Changements de configuration (clés API, SMTP)
    - Gestion des utilisateurs
    - Déclenchements de scans manuels
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Qui ───────────────────────────────────────────────────────────────
    user_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )  # Null pour les actions système

    # ─── Quoi ──────────────────────────────────────────────────────────────
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    # Ex: "auth.login.success", "auth.login.failure", "user.created",
    #     "apikey.updated", "scan.triggered", "smtp.configured"

    # ─── Contexte ──────────────────────────────────────────────────────────
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Ex: {"target_user": "bob@corp.com", "role_changed": "viewer→admin"}
    # ⚠️ JAMAIS de credentials ou données sensibles dans les details

    # ─── IP / Client ───────────────────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Timestamp ─────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} user={self.user_email}>"
