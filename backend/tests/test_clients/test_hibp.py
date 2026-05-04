"""
tests/test_clients/test_hibp.py

Tests unitaires pour le client HIBP.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.clients.hibp import HIBPClient
from app.core.sanitizer import DataSanitizer


class TestHIBPClient:
    
    @pytest.fixture
    def client(self) -> HIBPClient:
        return HIBPClient(api_key="fake_key", sanitizer=DataSanitizer())

    @pytest.mark.asyncio
    async def test_check_email_success(self, client: HIBPClient) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "Name": "Adobe",
                "Title": "Adobe",
                "Domain": "adobe.com",
                "BreachDate": "2013-10-04",
                "AddedDate": "2013-12-04T00:00:00Z",
                "ModifiedDate": "2013-12-04T00:00:00Z",
                "PwnCount": 152445165,
                "Description": "In October 2013, 153 million Adobe accounts were breached...",
                "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Adobe.png",
                "DataClasses": [
                    "Email addresses",
                    "Password hints",
                    "Passwords",
                    "Usernames"
                ],
                "IsVerified": True,
                "IsFabricated": False,
                "IsSensitive": False,
                "IsRetired": False,
                "IsSpamList": False
            }
        ]
        
        with patch.object(client, "_safe_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            findings = await client.check_email("test@example.com")
            
            assert len(findings) == 1
            assert findings[0].breach_name == "Adobe"
            assert findings[0].has_password is True
            assert findings[0].source == "hibp"

    @pytest.mark.asyncio
    async def test_check_email_not_found(self, client: HIBPClient) -> None:
        with patch.object(client, "_safe_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            findings = await client.check_email("safe@example.com")
            
            assert len(findings) == 0

    @pytest.mark.asyncio
    async def test_check_password_pwned(self, client: HIBPClient) -> None:
        mock_response = MagicMock()
        # "password" SHA1 is 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8
        # prefix: 5BAA6, suffix: 1E4C9B93F3F0682250B6CF8331B7EE68FD8
        mock_response.text = "1E4C9B93F3F0682250B6CF8331B7EE68FD8:9999999\nOTHER:123"
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            count = await client.check_password("password")
            
            assert count == 9999999

    @pytest.mark.asyncio
    async def test_check_password_safe(self, client: HIBPClient) -> None:
        mock_response = MagicMock()
        mock_response.text = "OTHER:123\nANOTHER:456"
        
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            count = await client.check_password("super_safe_password_12345!")
            
            assert count == 0
