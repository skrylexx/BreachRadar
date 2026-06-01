"""
BreachRadar WebUI — Schémas Auth (Pydantic)
===========================================
Validation des données d'entrée/sortie pour l'authentification.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Corps de la requête de connexion."""

    email: EmailStr
    password: str


class MFAVerifyRequest(BaseModel):
    """Vérification du code TOTP après la connexion password."""

    challenge_token: str  # Token temporaire Redis (valide 5 min)
    totp_code: str  # Code 6 chiffres ou code de secours 12 caractères

    @field_validator("totp_code")
    @classmethod
    def validate_totp_code(cls, v: str) -> str:
        # Autorise TOTP (6 chiffres) OU Backup Code (12 chars alphanum)
        if len(v) == 6 and v.isdigit():
            return v
        if len(v) == 12 and v.isalnum():
            return v
        raise ValueError("Must be a 6-digit TOTP or a 12-character backup code")


class MFASetupResponse(BaseModel):
    """Réponse lors de l'activation du MFA : QR code + secret de backup + codes de secours."""

    qrcode_base64: str  # "data:image/png;base64,..."
    manual_entry_key: str  # Clé manuelle pour les apps sans caméra
    backup_codes: list[str]  # 10 codes à usage unique


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
    mfa_challenge_token: str | None = None  # Seulement si MFA requis


class UserInfo(BaseModel):
    """Informations de l'utilisateur connecté (exposées au frontend)."""

    id: uuid.UUID
    email: str
    role: str
    mfa_enabled: bool
    mfa_required: bool
    last_login_at: datetime | None

    model_config = {"from_attributes": True}
