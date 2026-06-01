"""
tests/test_ransom_tracker.py

Tests unitaires du RansomwareTracker.

Couverture :
- Alerte immédiate déclenchée si domaine trouvé
- Retour vide si instance RansomLook inaccessible
- Déduplication multi-termes
- Gestion gracieuse d'une instance non disponible
- Alerte non bloquante même si le notifier échoue
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.engine.ransom_tracker import RansomwareTracker
from app.models.ransom import RansomFinding, RansomStats, RansomStatus


class TestRansomwareTrackerRun:
    """Tests de la méthode principale RansomwareTracker.run()."""

    @pytest.mark.asyncio
    async def test_domain_found_triggers_immediate_alert(
        self,
        mock_ransom_finding: RansomFinding,
        mock_ransom_stats_healthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """Si domaine trouvé : alerte notifier déclenchée IMMÉDIATEMENT."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        tracker = RansomwareTracker(client=client, notifier=mock_notifier)
        findings = await tracker.run("mondomaine.fr")

        # L'alerte doit avoir été envoyée
        mock_notifier.send_ransom_alert.assert_called_once_with(mock_ransom_finding)
        # Les findings sont retournés
        assert len(findings) == 1
        assert findings[0].group_name == "lockbit3"

    @pytest.mark.asyncio
    async def test_domain_not_found_returns_empty(
        self,
        mock_ransom_stats_healthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """Si domaine non trouvé : liste vide + pas d'alerte."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[])

        tracker = RansomwareTracker(client=client, notifier=mock_notifier)
        findings = await tracker.run("mondomaine.fr")

        assert findings == []
        mock_notifier.send_ransom_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_unhealthy_instance_handled_gracefully(
        self,
        mock_ransom_stats_unhealthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """Instance inaccessible → retour vide sans erreur ni crash."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_unhealthy)
        # check_domain NE doit pas être appelé si l'instance est inaccessible
        client.check_domain = AsyncMock(return_value=[])

        tracker = RansomwareTracker(client=client, notifier=mock_notifier)
        findings = await tracker.run("mondomaine.fr")

        assert findings == []
        client.check_domain.assert_not_called()
        mock_notifier.send_ransom_alert.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_findings_all_alerted(
        self,
        mock_ransom_stats_healthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """Plusieurs findings → une alerte par finding."""
        finding1 = RansomFinding(
            group_name="lockbit3",
            group_display_name="LockBit 3.0",
            victim_name="MonDomaine SA",
            discovered_at=datetime.fromisoformat("2025-01-14T14:32:00Z".replace("Z", "+00:00")),
            status=RansomStatus.LISTED,
            search_term_matched="mondomaine.fr",
        )
        finding2 = RansomFinding(
            group_name="play",
            group_display_name="Play",
            victim_name="MonDomaine Group",
            discovered_at=datetime.fromisoformat("2025-01-10T09:00:00Z".replace("Z", "+00:00")),
            status=RansomStatus.PUBLISHED,
            search_term_matched="MonDomaine",
        )

        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[finding1, finding2])

        tracker = RansomwareTracker(client=client, notifier=mock_notifier)
        findings = await tracker.run("mondomaine.fr")

        assert len(findings) == 2
        assert mock_notifier.send_ransom_alert.call_count == 2

    @pytest.mark.asyncio
    async def test_no_notifier_does_not_crash(
        self,
        mock_ransom_finding: RansomFinding,
        mock_ransom_stats_healthy: RansomStats,
    ) -> None:
        """Pas de notifier configuré → warning loggué mais pas de crash."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        # Aucun notifier passé
        tracker = RansomwareTracker(client=client, notifier=None)

        # Ne doit pas lever d'exception
        findings = await tracker.run("mondomaine.fr")
        assert len(findings) == 1

    @pytest.mark.asyncio
    async def test_notifier_failure_does_not_block(
        self,
        mock_ransom_finding: RansomFinding,
        mock_ransom_stats_healthy: RansomStats,
    ) -> None:
        """Échec du notifier → les findings sont quand même retournés."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        notifier = MagicMock()
        notifier.send_ransom_alert = AsyncMock(side_effect=Exception("SMTP error"))

        tracker = RansomwareTracker(client=client, notifier=notifier)

        # Ne doit pas lever d'exception même si le notifier échoue
        findings = await tracker.run("mondomaine.fr")
        assert len(findings) == 1


class TestRansomwareTrackerContext:
    """Tests de la méthode get_context()."""

    @pytest.mark.asyncio
    async def test_get_context_returns_stats(self, mock_ransom_stats_healthy: RansomStats) -> None:
        """get_context() retourne les stats de l'instance."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)

        tracker = RansomwareTracker(client=client)
        stats = await tracker.get_context()

        assert stats.is_healthy is True
        assert stats.groups_tracked == 124
