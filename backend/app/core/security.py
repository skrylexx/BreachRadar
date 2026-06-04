"""
BreachRadar WebUI — Security (JWT + Bcrypt + TOTP)
====================================================
All security functions centralized here.
"""

import base64
from datetime import UTC, datetime, timedelta
from io import BytesIO

import pyotp
import qrcode
import qrcode.image.svg
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ─── Password hashing (Bcrypt) ──────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str, is_admin: bool = False) -> tuple[bool, str]:
    """
    Validates password strength according to RBAC policy.

    Returns:
        (is_valid: bool, error_message: str)
    """
    min_length = settings.password_min_length_admin if is_admin else settings.password_min_length_viewer

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, ""


def is_password_rotation_required(last_password_change: datetime, password_length: int) -> bool:
    """
    Checks if password rotation is required.
    Exemption: if the password is longer than 24 characters.
    """
    if password_length >= settings.password_rotation_exemption_length:
        return False  # Free from rotation

    rotation_deadline = last_password_change + timedelta(days=settings.password_rotation_days)
    return datetime.now(UTC) > rotation_deadline


# ─── JWT Tokens ──────────────────────────────────────────────────────────────


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token (short duration: 15 min)."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Creates a JWT refresh token (long duration: 7 days)."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """Decodes and validates a JWT. Return None if invalid."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None


# ─── TOTP — MFA (RFC 6238) ───────────────────────────────────────────────────


def generate_totp_secret() -> str:
    """Generates a unique TOTP secret for a user."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Constructs the TOTP URI for authenticator apps (Google Auth, Authy...)."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="BreachRadar")


def generate_totp_qrcode_base64(secret: str, email: str) -> str:
    """
    Generates a base64 encoded QR code for MFA enrollment.
    Returns a string "data:image/png;base64,..." directly usable in HTML.
    """
    uri = get_totp_uri(secret, email)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def verify_totp(secret: str, code: str) -> bool:
    """
    Verifies a TOTP code with a tolerance window of ±1 interval (±30s).
    Protects against minor clock skews.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


# ─── Backup Codes ────────────────────────────────────────────────────────────


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generates a list of random backup codes."""
    import secrets
    import string

    codes = []
    for _ in range(count):
        # Format: 12 alphanumeric characters (ex: ABCD-EFGH-IJKL)
        code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        codes.append(code)
    return codes


# ─── Fernet encryption (Secrets in base) ────────────────────────────────────


def _get_fernet() -> Fernet:
    """
    Initializes the Fernet client with the settings key.
    If settings.encryption_key is not configured, a deterministic key is derived
    from jwt_secret_key (useful for dev/test).
    """
    if settings.encryption_key:
        return Fernet(settings.encryption_key.encode())

    # Simple deterministic derivation
    import base64
    import hashlib

    key_bytes = hashlib.sha256(settings.jwt_secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key_bytes))


def encrypt_secret(value: str) -> str:
    """Encrypts a character string (API key, SMTP password)."""
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_secret(token: str | None) -> str:
    """Decrypts a Fernet token."""
    if token is None:
        return ""
    f = _get_fernet()
    return f.decrypt(token.encode()).decode()
