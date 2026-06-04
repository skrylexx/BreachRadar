"""
BreachRadar WebUI — User Schemas (Pydantic)
==========================================
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Creation of a user (admin only)."""

    email: EmailStr
    password: str
    role: UserRole = UserRole.VIEWER


class UserRead(BaseModel):
    """User data exposed via the API."""

    id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    mfa_enabled: bool
    mfa_required: bool
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Partial update of a user."""

    role: UserRole | None = None
    is_active: bool | None = None


class UserList(BaseModel):
    """Paginated list of users."""

    items: list[UserRead]
    total: int
    page: int
    page_size: int
