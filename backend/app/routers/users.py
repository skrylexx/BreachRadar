"""
BreachRadar WebUI — Routeur Users (Admin only)
=====================================================
User CRUD: creation, listing, deactivation, role change.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, validate_password_strength
from app.dependencies.auth import AdminUser
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate

router = APIRouter()


@router.get("", response_model=UserList)
async def list_users(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
) -> UserList:
    """Lists all users (admin only)."""
    offset = (page - 1) * page_size

    result = await db.execute(select(User).offset(offset).limit(page_size))
    users = result.scalars().all()

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar_one()

    return UserList(
        items=[UserRead.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    body: UserCreate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Creates a new user."""
    # Check that the email does not already exist
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Validate the password according to the role
    is_admin = body.role == UserRole.ADMIN
    is_valid, error = validate_password_strength(body.password, is_admin=is_admin)
    if not is_valid:
        raise HTTPException(status_code=422, detail=error)

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        password_length=len(body.password),
    )
    db.add(user)
    await db.flush()

    # Audit log
    db.add(
        AuditLog(
            user_email=current_user.email,
            action="user.created",
            details={"target_email": body.email, "role": body.role.value},
            ip_address=request.client.host if request.client else None,
        )
    )

    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    request: Request,
    user_id: str,
    body: UserUpdate,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Updates the role or status of a user."""
    import uuid

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    changes = {}
    if body.role is not None:
        changes["role"] = f"{user.role.value}→{body.role.value}"
        user.role = body.role
    if body.is_active is not None:
        changes["is_active"] = f"{user.is_active}→{body.is_active}"
        user.is_active = body.is_active

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="user.updated",
            details={"target_email": user.email, **changes},
            ip_address=request.client.host if request.client else None,
        )
    )

    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes a user (soft delete — deactivation)."""
    import uuid

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user.is_active = False
    db.add(
        AuditLog(
            user_email=current_user.email,
            action="user.deactivated",
            details={"target_email": user.email},
            ip_address=request.client.host if request.client else None,
        )
    )


@router.post("/{user_id}/reset-mfa")
async def reset_mfa(
    request: Request,
    user_id: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Désactive le MFA pour un utilisateur (Admin only)."""
    import uuid

    target_id = uuid.UUID(user_id)
    if target_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot reset your own MFA")

    result = await db.execute(select(User).where(User.id == target_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.mfa_enabled = False
    user.mfa_secret = None
    user.token_version += 1

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="user.mfa.reset",
            details={"target_email": user.email},
            ip_address=request.client.host if request.client else None,
        )
    )

    await db.commit()
    return {"message": f"MFA has been reset for user {user.email}"}


@router.post("/{user_id}/require-mfa")
async def require_mfa(
    request: Request,
    user_id: str,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Force l'activation du MFA pour un utilisateur (Admin only)."""
    import uuid

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.mfa_required = True
    user.token_version += 1

    db.add(
        AuditLog(
            user_email=current_user.email,
            action="user.mfa.require",
            details={"target_email": user.email},
            ip_address=request.client.host if request.client else None,
        )
    )

    await db.commit()
    return {"message": f"MFA is now required for user {user.email}"}
