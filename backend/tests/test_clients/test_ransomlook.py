"""
tests/test_clients/test_ransomlook.py

Tests unitaires pour RansomLook Client.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.clients.ransomlook import RansomLookClient
from app.models.ransom import RansomStatus


class TestRansomLookClient:
    @pytest.fixture
    def client(self) -> RansomLookClient:
        # RansomLookClient prend ses paramètres depuis les settings globaux.
        # En test, on mocke les attributs après coup pour éviter de dépendre d'env vars réelles.
        with patch("app.clients.ransomlook.settings") as mock_settings:
            mock_settings.ransomlook_mode = "local"
            mock_settings.ransomlook_local_url = "http://localhost:8888"
            mock_settings.all_ransomlook_terms = ["extra_term"]
            mock_settings.request_timeout_seconds = 30
            return RansomLookClient()

    @pytest.mark.asyncio
    async def test_check_health_healthy(self, client: RansomLookClient) -> None:
        mock_data = {"groups": 10, "posts": 100, "last_update": "2025-01-01T00:00:00Z"}

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_data

            stats = await client.check_health()
            assert stats.is_healthy is True
            assert stats.groups_tracked == 10

    @pytest.mark.asyncio
    async def test_check_health_unhealthy(self, client: RansomLookClient) -> None:
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection error")

            stats = await client.check_health()
            assert stats.is_healthy is False

    @pytest.mark.asyncio
    async def test_check_domain_deduplication(self, client: RansomLookClient) -> None:
        mock_response_domain = [
            {
                "group_name": "lockbit3",
                "post_title": "MonDomaine",
                "published": "2025-01-01",
                "discovered": "2025-01-01",
            }
        ]
        # Le même résultat trouvé avec le terme supplémentaire
        mock_response_extra = [
            {
                "group_name": "lockbit3",
                "post_title": "MonDomaine",
                "published": "2025-01-01",
                "discovered": "2025-01-01",
            }
        ]

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            # Va être appelé pour 'test.com' puis pour 'extra_term'
            mock_get.side_effect = [mock_response_domain, mock_response_extra]

            findings = await client.check_domain("test.com")

            # Devrait être dédupliqué
            assert len(findings) == 1
            assert findings[0].group_name == "lockbit3"
            assert findings[0].status == RansomStatus.PUBLISHED
