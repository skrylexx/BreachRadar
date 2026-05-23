"""
BreachRadar WebUI — Schémas User (Pydantic)
==========================================
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Création d'un utilisateur (admin uniquement)."""
    email: EmailStr
    password: str
    role: UserRole = UserRole.VIEWER


class UserRead(BaseModel):
    """Données utilisateur exposées via l'API."""
    id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    mfa_enabled: bool
    mfa_required: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Mise à jour partielle d'un utilisateur."""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserList(BaseModel):
    """Liste paginée des utilisateurs."""
    items: list[UserRead]
    total: int
    page: int
    page_size: int
