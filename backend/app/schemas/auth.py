"""
BreachRadar WebUI — Auth Schemas (Pydantic)
===========================================
Validation of input/output data for authentication.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr
    password: str


class MFAVerifyRequest(BaseModel):
    """TOTP code verification after password login."""

    challenge_token: str  # Temporary Redis token (valid 5 min)
    totp_code: str  # 6-digit code or 12-character backup code

    @field_validator("totp_code")
    @classmethod
    def validate_totp_code(cls, v: str) -> str:
        # Allows TOTP (6 digits) OR Backup Code (12 chars alphanum)
        if len(v) == 6 and v.isdigit():
            return v
        if len(v) == 12 and v.isalnum():
            return v
        raise ValueError("Must be a 6-digit TOTP or a 12-character backup code")


class MFASetupResponse(BaseModel):
    """Response when activating MFA: QR code + backup secret + backup codes."""

    qrcode_base64: str  # "data:image/png;base64,..."
    manual_entry_key: str  # Manual key for apps without camera
    backup_codes: list[str]  # 10 single-use codes


class PasswordChangeRequest(BaseModel):
    """Password change."""

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
    """Email reset request."""

    email: EmailStr


class TokenResponse(BaseModel):
    """Response after successful login (tokens in HttpOnly cookies)."""

    message: str = "Login successful"
    requires_mfa: bool = False
    mfa_challenge_token: str | None = None  # Only if MFA required


class UserInfo(BaseModel):
    """Information of the logged-in user (exposed to the frontend)."""

    id: uuid.UUID
    email: str
    role: str
    mfa_enabled: bool
    mfa_required: bool
    last_login_at: datetime | None

    model_config = {"from_attributes": True}
