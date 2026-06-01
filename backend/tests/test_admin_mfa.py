"""
backend/tests/test_admin_mfa.py

Tests fonctionnels pour la gestion Admin du MFA.
"""

import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Set dummy environment variables
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "a" * 32
os.environ["INITIAL_ADMIN_EMAIL"] = "admin@example.com"
os.environ["INITIAL_ADMIN_PASSWORD"] = "CHANGE_ME_AdminPassword1!"
os.environ["TELEGRAM_API_ID"] = "0"

from app.core.config import get_settings

get_settings.cache_clear()

from app.core.database import get_db
from app.core.security import encrypt_secret, hash_password
from app.main import app
from app.models.user import User, UserRole

# Disable rate limiting
app.state.limiter.enabled = False


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


from app.dependencies.auth import require_admin


async def override_require_admin():
    print("DEBUG: override_require_admin CALLED")
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True,
        token_version=1,
    )


@pytest.fixture(autouse=True)
def mock_redis_helpers():
    """Mock automatique des helpers Redis."""
    with (
        patch("app.routers.auth.increment_mfa_failures", new_callable=AsyncMock) as m1,
        patch("app.routers.auth.get_mfa_failures", new_callable=AsyncMock) as m2,
        patch("app.routers.auth.reset_mfa_failures", new_callable=AsyncMock) as m3,
    ):
        m2.return_value = 0
        yield (m1, m2, m3)


@pytest.mark.asyncio
async def test_admin_reset_mfa_success(async_client):
    """Teste le reset MFA par un admin."""
    app.dependency_overrides[require_admin] = override_require_admin

    target_user_id = uuid.uuid4()
    target_user = User(
        id=target_user_id,
        email="viewer@example.com",
        role=UserRole.VIEWER,
        mfa_enabled=True,
        mfa_secret=encrypt_secret("SECRET"),
        is_active=True,
        token_version=1,
    )

    mock_db = AsyncMock()
    mock_res_target = MagicMock()
    mock_res_target.scalar_one_or_none.return_value = target_user
    mock_db.execute.return_value = mock_res_target

    app.dependency_overrides[get_db] = lambda: mock_db

    response = await async_client.post(f"/api/v1/users/{target_user_id}/reset-mfa")

    assert response.status_code == 200
    assert target_user.mfa_enabled is False
    assert target_user.mfa_secret is None


@pytest.mark.asyncio
async def test_admin_require_mfa_success(async_client):
    """Teste l'obligation MFA par un admin."""
    app.dependency_overrides[require_admin] = override_require_admin

    target_user_id = uuid.uuid4()
    target_user = User(
        id=target_user_id,
        email="viewer@example.com",
        role=UserRole.VIEWER,
        mfa_enabled=False,
        mfa_required=False,
        is_active=True,
        token_version=1,
    )

    mock_db = AsyncMock()
    mock_res_target = MagicMock()
    mock_res_target.scalar_one_or_none.return_value = target_user
    mock_db.execute.return_value = mock_res_target

    app.dependency_overrides[get_db] = lambda: mock_db

    response = await async_client.post(f"/api/v1/users/{target_user_id}/require-mfa")

    assert response.status_code == 200
    assert target_user.mfa_required is True


@pytest.mark.asyncio
async def test_login_with_mfa_required(async_client):
    """Teste que mfa_required=True force le passage par le flux MFA au login."""
    user = User(
        id=uuid.uuid4(),
        email="required@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.VIEWER,
        mfa_enabled=False,
        mfa_required=True,
        is_active=True,
        password_length=12,
        token_version=1,
        last_password_change=datetime.now(UTC),
    )

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("app.routers.auth.store_mfa_challenge", new_callable=AsyncMock) as mock_store:
        login_data = {"email": "required@example.com", "password": "Password123!"}
        response = await async_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        assert response.json()["requires_mfa"] is True
        mock_store.assert_called_once()
