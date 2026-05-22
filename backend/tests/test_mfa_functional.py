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

import pytest
import pyotp
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User, UserRole
from app.core.security import hash_password
from app.core.database import get_db

# Disable rate limiting for tests
app.state.limiter.enabled = False

# Global DB Mock
global_mock_db = AsyncMock()

async def override_get_db():
    yield global_mock_db

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

from datetime import datetime, timezone

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
        mfa_secret=secret,
        is_active=True,
        password_length=12,
        last_password_change=datetime.now(timezone.utc)
    )

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
            totp = pyotp.TOTP(mock_user.mfa_secret)
            valid_code = totp.now()
            
            # Mock verify_mfa_challenge to return user_id
            mock_verify.return_value = str(mock_user.id)
            
            verify_data = {
                "challenge_token": challenge_token,
                "totp_code": valid_code
            }
            
            response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
            
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
            "totp_code": "000000" # Invalid code
        }
        
        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid TOTP code"

@pytest.mark.asyncio
async def test_mfa_verify_expired_challenge(async_client):
    """Teste l'échec de vérification MFA avec un challenge expiré."""
    
    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = None # Expired or invalid
        
        verify_data = {
            "challenge_token": "expired_token",
            "totp_code": "123456"
        }
        
        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired challenge token"

@pytest.mark.asyncio
async def test_mfa_verify_rate_limiting(async_client):
    """Teste le rate limiting sur l'endpoint de vérification MFA."""
    # Re-enable rate limiting just for this test
    app.state.limiter.enabled = True
    
    with patch("app.routers.auth.verify_mfa_challenge", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = str(uuid.uuid4())
        
        verify_data = {
            "challenge_token": "limit_test_token",
            "totp_code": "123456"
        }
        
        # Le limiteur est à 10/minute dans le code
        for i in range(10):
            response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
            # On ignore le résultat métier, on veut juste voir si ça passe le limiter
            # Note: Comme on mock verify_totp à True ou False, ça retournera 401 ou 200
            # Mais après 10, ça devrait être 429
            if response.status_code == 429:
                break
        
        # 11ème appel
        response = await async_client.post("/api/v1/auth/mfa/verify", json=verify_data)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.text
        
    # Disable back for other tests
    app.state.limiter.enabled = False

# Utilitaires pour mocker SQLAlchemy
from unittest.mock import MagicMock
