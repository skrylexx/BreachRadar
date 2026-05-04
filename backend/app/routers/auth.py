"""
BreachRadar WebUI — Routeur Auth
=================================
Endpoints : /auth/login, /auth/logout, /auth/refresh,
            /auth/me, /auth/mfa/setup, /auth/mfa/verify,
            /auth/password/change
"""

import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import (
    blacklist_token,
    is_token_blacklisted,
    store_mfa_challenge,
    verify_mfa_challenge,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_totp_qrcode_base64,
    generate_totp_secret,
    hash_password,
    is_password_rotation_required,
    validate_password_strength,
    verify_password,
    verify_totp,
)
from app.dependencies.auth import CurrentUser, ViewerUser
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserInfo,
)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# ─── Constantes Cookie ────────────────────────────────────────────────────────
COOKIE_SECURE = settings.environment == "production"
COOKIE_SAMESITE = "lax"


def _set_auth_cookies(response: Response, user_id: uuid.UUID, email: str) -> None:
    """Pose les cookies HttpOnly JWT (access + refresh)."""
    jti = secrets.token_urlsafe(16)
    access_token = create_access_token({"sub": str(user_id), "email": email, "jti": jti})
    refresh_token = create_refresh_token({"sub": str(user_id), "email": email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=settings.jwt_refresh_token_expire_days * 86400,
        path="/auth/refresh",  # Restreindre le refresh au seul endpoint dédié
    )


async def _log_action(
    db: AsyncSession,
    action: str,
    request: Request,
    user_email: str | None = None,
    details: dict | None = None,
) -> None:
    """Écrit une entrée dans l'audit log."""
    log = AuditLog(
        user_email=user_email,
        action=action,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    await db.flush()


# ─── POST /auth/login ─────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authentification en deux étapes :
    1. Validation email + password
    2. Si MFA activé → retourne un challenge_token temporaire pour /mfa/verify
       Sinon → pose les cookies JWT directement
    """
    # Recherche utilisateur (timing constant contre l'énumération d'emails)
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Vérification password (même si user=None pour éviter timing attack)
    dummy_hash = "$2b$12$invalidhashfortimingnnnnnnnnnnnnnnnnnnnnn"
    password_ok = verify_password(
        body.password,
        user.hashed_password if user else dummy_hash,
    )

    if not user or not password_ok or not user.is_active:
        await _log_action(db, "auth.login.failure", request, body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Vérifier la rotation du mot de passe
    if is_password_rotation_required(user.last_password_change, user.password_length):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password expired. Please reset your password.",
            headers={"X-Password-Expired": "true"},
        )

    # MFA requis ?
    if user.mfa_enabled:
        challenge_token = secrets.token_urlsafe(32)
        await store_mfa_challenge(str(user.id), challenge_token)
        await _log_action(db, "auth.mfa.challenge_issued", request, user.email)
        return TokenResponse(requires_mfa=True, mfa_challenge_token=challenge_token)

    # Connexion directe (pas de MFA)
    _set_auth_cookies(response, user.id, user.email)
    user.last_login_at = datetime.now(timezone.utc)
    await _log_action(db, "auth.login.success", request, user.email)
    return TokenResponse()


# ─── POST /auth/mfa/verify ────────────────────────────────────────────────────
@router.post("/mfa/verify", response_model=TokenResponse)
@limiter.limit("10/minute")
async def mfa_verify(
    request: Request,
    response: Response,
    body: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Valide le code TOTP après le challenge password."""
    # Retrouver l'utilisateur via le challenge token (Redis)
    # Note : le challenge_token est stocké avec le user_id comme clé
    # On doit itérer ou avoir une structure inversée
    # Solution : encoder le user_id dans le challenge_token signé
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="MFA verify endpoint — implementation in next iteration",
    )


# ─── POST /auth/logout ────────────────────────────────────────────────────────
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Révoque le token courant (blacklist Redis) et supprime les cookies."""
    access_token = request.cookies.get("access_token")
    if access_token:
        payload = decode_token(access_token)
        if payload and (jti := payload.get("jti")):
            # Blacklister jusqu'à l'expiration naturelle du token
            exp = payload.get("exp", 0)
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(exp - now, 0)
            await blacklist_token(jti, ttl)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth/refresh")
    await _log_action(db, "auth.logout", request, current_user.email)
    return {"message": "Logged out successfully"}


# ─── GET /auth/me ─────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserInfo)
async def get_me(current_user: ViewerUser) -> User:
    """Retourne les informations de l'utilisateur connecté."""
    return current_user


# ─── POST /auth/mfa/setup ─────────────────────────────────────────────────────
@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MFASetupResponse:
    """
    Génère un secret TOTP et retourne le QR code pour l'enrôlement.
    L'utilisateur doit confirmer avec /mfa/confirm avant activation.
    """
    secret = generate_totp_secret()
    # Stocker temporairement dans l'utilisateur (non activé)
    current_user.mfa_secret = secret
    # Note: mfa_enabled reste False jusqu'à confirmation

    return MFASetupResponse(
        qrcode_base64=generate_totp_qrcode_base64(secret, current_user.email),
        manual_entry_key=secret,
    )


# ─── POST /auth/password/change ───────────────────────────────────────────────
@router.post("/password/change")
async def change_password(
    request: Request,
    body: PasswordChangeRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Changement de mot de passe authentifié."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    is_admin = current_user.role.value == "admin"
    is_valid, error = validate_password_strength(body.new_password, is_admin=is_admin)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    current_user.hashed_password = hash_password(body.new_password)
    current_user.last_password_change = datetime.now(timezone.utc)
    current_user.password_length = len(body.new_password)

    await _log_action(db, "auth.password.changed", request, current_user.email)
    return {"message": "Password changed successfully"}


# ─── GET /health (quick auth check) ──────────────────────────────────────────
@router.get("/status")
async def auth_status(current_user: ViewerUser) -> dict:
    """Vérifie si le token est valide — utilisé par le frontend."""
    return {
        "authenticated": True,
        "email": current_user.email,
        "role": current_user.role.value,
    }
