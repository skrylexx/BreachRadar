"""
BreachRadar WebUI — Dépendances Auth & RBAC
============================================
Injection de dépendances FastAPI pour la vérification JWT et les rôles.
"""

import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import is_token_blacklisted
from app.core.security import decode_token
from app.models.user import User, UserRole


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency : extrait et valide le JWT depuis le cookie HttpOnly.
    Lève 401 si le token est absent, invalide ou révoqué.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        raise credentials_exception

    # Décoder le JWT
    payload = decode_token(access_token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    # Vérifier la blacklist Redis (logout)
    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise credentials_exception

    # Récupérer l'utilisateur en DB
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency : réservé aux administrateurs."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def require_viewer(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency : tout utilisateur authentifié (Admin OU Viewer)."""
    # Les deux rôles ont accès en lecture
    return current_user


# ─── Types annotés pour injection propre ─────────────────────────────────────
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
ViewerUser = Annotated[User, Depends(require_viewer)]
