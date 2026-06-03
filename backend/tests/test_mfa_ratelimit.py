"""
backend/tests/test_mfa_ratelimit.py

Test isolé pour le rate limiting MFA.
"""

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pyotp
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
from app.core.security import encrypt_secret
from app.main import app
from app.models.user import User

# Global Mock User
MOCK_USER_ID = uuid.uuid4()


async def override_get_db():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_user = User(
        id=MOCK_USER_ID,
        email="limit@example.com",
        is_active=True,
        token_version=1,
        mfa_enabled=True,
        mfa_secret=encrypt_secret(pyotp.random_base32()),
    )
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_user
    mock_db.execute.return_value = mock_res
    yield mock_db


@pytest.fixture
async def async_client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_mfa_verify_rate_limiting(async_client):
    """Teste le rate limiting sur l'endpoint de vérification MFA."""
    # Re-enable rate limiting just for this test
    app.state.limiter.enabled = True

    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = str(MOCK_USER_ID)

        # Mock failure tracking helpers to avoid ConnectionError
        with (
            patch("app.routers.auth.get_mfa_failures", new_callable=AsyncMock) as m_get,
            patch("app.routers.auth.increment_mfa_failures", new_callable=AsyncMock),
        ):
            m_get.return_value = 0

            verify_data = {"challenge_token": "limit_test_token", "totp_code": "123456"}

            # Le limiteur est à 10/minute dans le code
            for _i in range(10):
                response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
                if response.status_code == 429:
                    break

            # 11ème appel
            response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.text

    # Disable back
    app.state.limiter.enabled = False
