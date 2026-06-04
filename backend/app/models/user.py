"""
BreachRadar WebUI — User Model (SQLAlchemy)
=============================================================
User management with RBAC and password policy.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(enum.StrEnum):
    """RBAC roles available."""

    ADMIN = "admin"  # API key management, users, SMTP — can trigger scans
    VIEWER = "viewer"  # Read and export reports only


class User(Base):
    """Primary user model."""

    __tablename__ = "users"

    # ─── Identity ───────────────────────────── ─────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # ─── RBAC ─────────────────────────────── ───────────────────────────────
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.VIEWER,
    )

    # ─── Status ────────────────────────────── ──────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # ─── MFA (TOTP) ──────────────────────────── ────────────────────────────
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mfa_backup_codes: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # ─── Password management ──────────────────── ─────────────────────
    last_password_change: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    # Length of last MDP to calculate rotation exemption
    password_length: Mapped[int] = mapped_column(default=0, nullable=False)

    # ─── Metadata ─────────────────────────── ────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
