"""
backend/tests/test_mfa_functional.py

Tests fonctionnels du flux MFA :
1. Login -> Challenge
2. Verify -> Success (Cookies)
3. Verify -> Failure (Wrong code)
4. Verify -> Failure (Expired challenge)
"""

import os

# Set dummy environment variables for Pydantic Settings before any other imports
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "a" * 32
os.environ["INITIAL_ADMIN_EMAIL"] = "admin@example.com"
os.environ["INITIAL_ADMIN_PASSWORD"] = "CHANGE_ME_AdminPassword1!"
os.environ["TELEGRAM_API_ID"] = "0"

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pyotp
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings

get_settings.cache_clear()

from app.core.database import get_db
from app.core.security import decrypt_secret, encrypt_secret, hash_password
from app.main import app
from app.models.user import User, UserRole

# Disable rate limiting for tests
app.state.limiter.enabled = False

# Global DB Mock
global_mock_db = AsyncMock()


async def override_get_db():
    yield global_mock_db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db_mock():
    """Réinitialise le mock de la base de données entre chaque test."""
    global_mock_db.reset_mock()
    global_mock_db.execute = AsyncMock()
    global_mock_db.commit = AsyncMock()
    global_mock_db.add = AsyncMock()
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


from datetime import UTC, datetime


@pytest.fixture
def mock_user():
    user_id = uuid.uuid4()
    secret = pyotp.random_base32()
    return User(
        id=user_id,
        email="test@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN,
        mfa_enabled=True,
        mfa_secret=encrypt_secret(secret),
        is_active=True,
        password_length=12,
        token_version=1,
        last_password_change=datetime.now(UTC),
    )


@pytest.fixture(autouse=True)
def mock_redis_helpers():
    """Mock automatique des helpers Redis pour éviter ConnectionError."""
    with (
        patch("app.routers.auth.increment_mfa_failures", new_callable=AsyncMock) as m1,
        patch("app.routers.auth.get_mfa_failures", new_callable=AsyncMock) as m2,
        patch("app.routers.auth.reset_mfa_failures", new_callable=AsyncMock) as m3,
    ):
        m2.return_value = 0  # Pas d'échec par défaut
        yield (m1, m2, m3)


@pytest.mark.asyncio
async def test_mfa_login_and_verify_success(async_client, mock_user):
    """Teste le flux complet MFA réussi."""

    # Mocking the select(User) result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    global_mock_db.execute.return_value = mock_result

    # Mock Redis
    with patch("app.routers.auth.store_mfa_challenge", new_callable=AsyncMock) as mock_store:
        with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
            # 1. Login
            login_data = {"email": "test@example.com", "password": "Password123!"}
            response = await async_client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == 200
            data = response.json()
            assert data["requires_mfa"] is True
            assert "mfa_challenge_token" in data
            challenge_token = data["mfa_challenge_token"]

            # Verify store was called
            mock_store.assert_called_once_with(str(mock_user.id), challenge_token)

            # 2. Verify MFA
            totp = pyotp.TOTP(decrypt_secret(mock_user.mfa_secret))
            valid_code = totp.now()

            # Mock verify_mfa_challenge to return user_id
            mock_verify.return_value = str(mock_user.id)

            verify_data = {"challenge_token": challenge_token, "totp_code": valid_code}

            response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
            if response.status_code != 200:
                print(f"DEBUG: {response.status_code} - {response.text}")
            assert response.status_code == 200
            assert response.cookies.get("access_token") is not None
            assert response.json()["message"] == "Login successful"


@pytest.mark.asyncio
async def test_mfa_verify_invalid_code(async_client, mock_user):
    """Teste l'échec de vérification MFA avec un mauvais code."""

    # Mocking the select(User) result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    global_mock_db.execute.return_value = mock_result

    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = str(mock_user.id)

        verify_data = {
            "challenge_token": "some_token",
            "totp_code": "000000",  # Invalid code
        }

        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid verification code"


@pytest.mark.asyncio
async def test_mfa_verify_expired_challenge(async_client):
    """Teste l'échec de vérification MFA avec un challenge expiré."""

    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = None  # Expired or invalid

        verify_data = {"challenge_token": "expired_token", "totp_code": "123456"}

        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired challenge token"


@pytest.mark.asyncio
async def test_mfa_disable_success(async_client, mock_user):
    """Teste la désactivation réussie du MFA par l'utilisateur."""
    # Mocking CurrentUser dependency
    from app.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_user

    totp = pyotp.TOTP(decrypt_secret(mock_user.mfa_secret))
    valid_code = totp.now()

    disable_data = {"totp_code": valid_code}

    response = await async_client.post("/api/v1/auth/mfa/disable", json=disable_data)

    assert response.status_code == 200
    assert mock_user.mfa_enabled is False
    assert mock_user.mfa_secret is None
    assert response.json()["message"] == "MFA disabled successfully"
    del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_mfa_disable_invalid_code(async_client, mock_user):
    """Teste l'échec de désactivation du MFA avec un mauvais code."""
    from app.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_user

    disable_data = {"totp_code": "000000"}

    response = await async_client.post("/api/v1/auth/mfa/disable", json=disable_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid TOTP code"
    assert mock_user.mfa_enabled is True  # Toujours actif
    del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_mfa_verify_backup_code_success(async_client, mock_user):
    """Teste la connexion réussie via un code de secours."""
    # Préparer un code de secours haché
    backup_code = "1234567890AB"
    mock_user.mfa_backup_codes = [hash_password(backup_code)]

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    global_mock_db.execute.return_value = mock_result

    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = str(mock_user.id)

        verify_data = {
            "challenge_token": "backup_test_token",
            "totp_code": backup_code,  # Saisie du backup code au lieu du TOTP
        }

        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)

        assert response.status_code == 200
        assert response.json()["message"] == "Login successful"
        # Le code doit être consommé
        assert len(mock_user.mfa_backup_codes) == 0


# Utilitaires pour mocker SQLAlchemy
