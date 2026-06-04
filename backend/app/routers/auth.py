"""
BreachRadar WebUI — Auth Router
==================================
Endpoints: /auth/login, /auth/logout, /auth/refresh,
            /auth/me, /auth/mfa/setup, /auth/mfa/verify,
            /auth/password/change
"""

import logging
import secrets
import uuid

logger = logging.getLogger(__name__)
from datetime import UTC, datetime
from typing import Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import (
    blacklist_token,
    get_mfa_failures,
    increment_mfa_failures,
    reset_mfa_failures,
    store_mfa_challenge,
    verify_mfa_challenge,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decrypt_secret,
    encrypt_secret,
    generate_backup_codes,
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

# ─── Cookie Constants ──────────────────────────── ────────────────────────────
COOKIE_SECURE = settings.environment == "production"
COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"


def _set_auth_cookies(response: Response, user_id: uuid.UUID, email: str, role: str, token_version: int) -> None:
    """Sets HttpOnly JWT cookies (access + refresh)."""
    jti = secrets.token_urlsafe(16)
    access_token = create_access_token(
        {"sub": str(user_id), "email": email, "role": role, "jti": jti, "v": token_version}
    )
    refresh_token = create_refresh_token({"sub": str(user_id), "email": email, "v": token_version})

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
        path="/api/v1/auth/refresh",  # Restrict the refresh to the dedicated endpoint only
    )


async def _log_action(
    db: AsyncSession,
    action: str,
    request: Request,
    user_email: str | None = None,
    details: dict | None = None,
) -> None:
    """Writes an entry to the audit log."""
    log = AuditLog(
        user_email=user_email,
        action=action,
        details=details,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    await db.flush()


# ─── POST /auth/login ──────────────────────────── ─────────────────────────────
@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Two-step authentication:
    1. Email validation + password
    2. If MFA enabled → returns a temporary challenge_token for /mfa/verify
       Otherwise → set JWT cookies directly
    """
    # User search (constant timing versus email enumeration)
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Password verification (even if user=None to avoid timing attack)
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

    # Check password rotation
    if is_password_rotation_required(user.last_password_change, user.password_length):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password expired. Please reset your password.",
            headers={"X-Password-Expired": "true"},
        )

    # MFA required?
    if user.mfa_enabled or user.mfa_required:
        challenge_token = secrets.token_urlsafe(32)
        await store_mfa_challenge(str(user.id), challenge_token)
        await _log_action(db, "auth.mfa.challenge_issued", request, user.email)
        return TokenResponse(requires_mfa=True, mfa_challenge_token=challenge_token)

    # Direct connection (no MFA)
    _set_auth_cookies(response, user.id, user.email, user.role.value, user.token_version)
    user.last_login_at = datetime.now(UTC)
    await _log_action(db, "auth.login.success", request, user.email)
    return TokenResponse()


@router.post("/mfa/verify", response_model=TokenResponse)
@limiter.limit("10/minute")
async def mfa_verify(
    request: Request,
    response: Response,
    body: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Validate the TOTP code after the password challenge."""
    # Find the user via the token challenge (Redis)
    user_id = await verify_mfa_challenge(body.challenge_token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired challenge token",
        )

    # TOTP Brute Force Protection
    fail_count = await get_mfa_failures(user_id)
    if fail_count >= 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Too many failed MFA attempts. Please try again in 15 minutes.",
        )

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Code verification (standard TOTP or emergency Backup Code)
    is_valid = False
    is_backup_used = False

    # Accept backup codes (12 characters)
    if len(body.totp_code) == 12:
        # Attempt via emergency code
        if user.mfa_backup_codes:
            for i, hashed in enumerate(user.mfa_backup_codes):
                if verify_password(body.totp_code, hashed):
                    user.mfa_backup_codes.pop(i)
                    from sqlalchemy.orm.attributes import flag_modified

                    flag_modified(user, "mfa_backup_codes")
                    is_valid = True
                    is_backup_used = True
                    # If a backup code is used, the MFA is forced to reset
                    user.mfa_enabled = False
                    user.mfa_required = True
                    user.token_version += 1  # Invalidate other sessions for security
                    break
    else:
        # Attempt via standard TOTP
        is_valid = verify_totp(decrypt_secret(cast(str, user.mfa_secret)), body.totp_code)

    if not is_valid:
        await increment_mfa_failures(user_id)
        await _log_action(db, "auth.mfa.failure", request, user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code",
        )

    # Success: Brute-force cleaning and installation of JWT cookies
    await reset_mfa_failures(user_id)
    _set_auth_cookies(response, user.id, user.email, user.role.value, user.token_version)
    user.last_login_at = datetime.now(UTC)

    audit_action = "auth.mfa.backup_success" if is_backup_used else "auth.mfa.success"
    await _log_action(db, audit_action, request, user.email)
    await db.commit()

    return TokenResponse()


# ─── POST /auth/logout ──────────────────────────── ────────────────────────────
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revokes the current token (Redis blacklist) and deletes cookies."""
    access_token = request.cookies.get("access_token")
    if access_token:
        payload = decode_token(access_token)
        if payload and (jti := payload.get("jti")):
            # Blacklist until the natural expiration of the token
            exp = payload.get("exp", 0)
            now = int(datetime.now(UTC).timestamp())
            ttl = max(exp - now, 0)
            await blacklist_token(jti, ttl)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    await _log_action(db, "auth.logout", request, current_user.email)
    return {"message": "Logged out successfully"}


# ─── GET /auth/me ────────────────────────────── ───────────────────────────────
@router.get("/me", response_model=UserInfo)
async def get_me(current_user: ViewerUser) -> User:
    """Returns the information of the logged in user."""
    return current_user


# ─── POST /auth/mfa/setup ────────────────────────── ───────────────────────────
@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MFASetupResponse:
    """
    Generates a TOTP secret and returns the QR code for enrollment.
    The user must confirm with /mfa/confirm before activation.
    """
    secret = generate_totp_secret()
    # Store temporarily in user (not enabled)
    current_user.mfa_secret = encrypt_secret(secret)

    # Generate 10 backup codes
    backup_codes = generate_backup_codes(10)
    # Store chopped (single use)
    current_user.mfa_backup_codes = [hash_password(c) for c in backup_codes]

    await db.flush()

    return MFASetupResponse(
        qrcode_base64=generate_totp_qrcode_base64(secret, current_user.email),
        manual_entry_key=secret,
        backup_codes=backup_codes,
    )


@router.post("/mfa/confirm", response_model=UserInfo)
async def mfa_confirm(
    body: dict,
    response: Response,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validates the first TOTP code to permanently activate MFA."""
    code = body.get("totp_code")
    if not code or not verify_totp(decrypt_secret(cast(str, current_user.mfa_secret)), code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    current_user.mfa_enabled = True
    current_user.mfa_required = False  # If we come from a reset via backup code
    current_user.token_version += 1

    # Refresh cookies with the new version
    _set_auth_cookies(
        response,
        current_user.id,
        current_user.email,
        current_user.role.value,
        current_user.token_version,
    )

    await db.commit()
    return current_user


@router.post("/mfa/disable", response_model=UserInfo)
async def mfa_disable(
    request: Request,
    response: Response,
    body: dict,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Disables user MFA (requires TOTP code)."""
    if not current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is not enabled")

    code = body.get("totp_code")
    if not code or not verify_totp(decrypt_secret(cast(str, current_user.mfa_secret)), code):
        await _log_action(db, "auth.mfa.disable.failure", request, current_user.email)
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    if current_user.mfa_required is None:
        current_user.mfa_required = False
    current_user.token_version += 1

    # Refresh cookies with the new version
    _set_auth_cookies(
        response,
        current_user.id,
        current_user.email,
        current_user.role.value,
        current_user.token_version,
    )

    await _log_action(db, "auth.mfa.disable.success", request, current_user.email)
    await db.commit()
    return current_user


# ─── POST /auth/password/change ─────────────────────── ────────────────────────
@router.post("/password/change", response_model=UserInfo)
async def change_password(
    request: Request,
    response: Response,
    body: PasswordChangeRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authenticated password change."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    is_admin = current_user.role.value == "admin"
    is_valid, error = validate_password_strength(body.new_password, is_admin=is_admin)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    current_user.hashed_password = hash_password(body.new_password)
    current_user.last_password_change = datetime.now(UTC)
    current_user.password_length = len(body.new_password)
    current_user.token_version += 1

    # Refresh cookies with the new version
    _set_auth_cookies(
        response,
        current_user.id,
        current_user.email,
        current_user.role.value,
        current_user.token_version,
    )

    await _log_action(db, "auth.password.changed", request, current_user.email)
    await db.commit()
    return current_user


# ─── GET /health (quick auth check) ───────────────────── ─────────────────────
@router.get("/status")
async def auth_status(current_user: ViewerUser) -> dict:
    """Checks if the token is valid — used by the frontend."""
    return {
        "authenticated": True,
        "email": current_user.email,
        "role": current_user.role.value,
    }
