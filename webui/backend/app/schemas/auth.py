"""
BreachRadar WebUI — Schémas Auth (Pydantic)
===========================================
Validation des données d'entrée/sortie pour l'authentification.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.core.config import settings


class LoginRequest(BaseModel):
    """Corps de la requête de connexion."""
    email: EmailStr
    password: str


class MFAVerifyRequest(BaseModel):
    """Vérification du code TOTP après la connexion password."""
    challenge_token: str  # Token temporaire Redis (valide 5 min)
    totp_code: str        # Code 6 chiffres de l'app authenticator

    @field_validator("totp_code")
    @classmethod
    def validate_totp_code(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("TOTP code must be exactly 6 digits")
        return v


class MFASetupResponse(BaseModel):
    """Réponse lors de l'activation du MFA : QR code + secret de backup."""
    qrcode_base64: str    # "data:image/png;base64,..."
    manual_entry_key: str # Clé manuelle pour les apps sans caméra


class PasswordChangeRequest(BaseModel):
    """Changement de mot de passe."""
    current_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password_confirm")
    @classmethod
    def passwords_match(cls, v: str, values) -> str:
        if "new_password" in values.data and v != values.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordResetRequest(BaseModel):
    """Demande de reset par email."""
    email: EmailStr


class TokenResponse(BaseModel):
    """Réponse après connexion réussie (tokens dans cookies HttpOnly)."""
    message: str = "Login successful"
    requires_mfa: bool = False
    mfa_challenge_token: Optional[str] = None  # Seulement si MFA requis


class UserInfo(BaseModel):
    """Informations de l'utilisateur connecté (exposées au frontend)."""
    id: uuid.UUID
    email: str
    role: str
    mfa_enabled: bool
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}
