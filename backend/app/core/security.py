"""
BreachRadar WebUI — Sécurité (JWT + Bcrypt + TOTP)
====================================================
Toutes les fonctions de sécurité centralisées ici.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ─── Hachage des mots de passe (Bcrypt) ──────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str, is_admin: bool = False) -> tuple[bool, str]:
    """
    Valide la force du mot de passe selon la politique RBAC.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    min_length = (
        settings.password_min_length_admin if is_admin
        else settings.password_min_length_viewer
    )

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
    Vérifie si la rotation du mot de passe est requise.
    Exemption : si le mot de passe fait plus de 24 caractères.
    """
    if password_length >= settings.password_rotation_exemption_length:
        return False  # Exempt de rotation

    rotation_deadline = last_password_change + timedelta(days=settings.password_rotation_days)
    return datetime.now(timezone.utc) > rotation_deadline


# ─── JWT Tokens ──────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un JWT access token (durée courte : 15 min)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Crée un JWT refresh token (durée longue : 7 jours)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Décode et valide un JWT. Retourne None si invalide."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None


# ─── TOTP — MFA (RFC 6238) ───────────────────────────────────────────────────

def generate_totp_secret() -> str:
    """Génère un secret TOTP unique pour un utilisateur."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Construit l'URI TOTP pour les apps authenticator (Google Auth, Authy...)."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="BreachRadar")


def generate_totp_qrcode_base64(secret: str, email: str) -> str:
    """
    Génère un QR code encodé en base64 pour l'enrôlement MFA.
    Retourne une chaîne "data:image/png;base64,..." directement utilisable en HTML.
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
    Vérifie un code TOTP avec une fenêtre de tolérance de ±1 intervalle (±30s).
    Protège contre les décalages d'horloge mineurs.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
