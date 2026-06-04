"""
tests/test_ransom_tracker.py

Unit tests for the RansomwareTracker.

Coverage:
- Immediate alert triggered if domain found
- Empty return if RansomLook instance is inaccessible
- Multi-term deduplication
- Graceful management of an unavailable instance
- Non-blocking alert even if the notifier fails
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.engine.ransom_tracker import RansomwareTracker
from app.models.ransom import RansomFinding, RansomStats, RansomStatus


class TestRansomwareTrackerRun:
    """Tests for the main RansomwareTracker.run() method."""

    @pytest.mark.asyncio
    async def test_domain_found_triggers_immediate_alert(
        self,
        mock_ransom_finding: RansomFinding,
        mock_ransom_stats_healthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """If domain found: notifier alert triggered IMMEDIATELY."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        tracker = RansomwareTracker(client=client, notifier=mock_notifier)
        findings = await tracker.run("mondomaine.fr")

        # The alert must have been sent
        mock_notifier.send_ransom_alert.assert_called_once_with(mock_ransom_finding)
        # The findings are returned
        assert len(findings) == 1
        assert findings[0].group_name == "lockbit3"

    @pytest.mark.asyncio
    async def test_domain_not_found_returns_empty(
        self,
        mock_ransom_stats_healthy: RansomStats,
        mock_notifier: MagicMock,
    ) -> None:
        """If domain not found: empty list + no alert."""
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
        """Inaccessible instance → empty return without error or crash."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_unhealthy)
        # check_domain MUST NOT be called if the instance is inaccessible
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
        """Several findings → one alert per finding."""
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
        """No configured notifier → warning logged but no crash."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        # No notifier passed
        tracker = RansomwareTracker(client=client, notifier=None)

        # Must not raise an exception
        findings = await tracker.run("mondomaine.fr")
        assert len(findings) == 1

    @pytest.mark.asyncio
    async def test_notifier_failure_does_not_block(
        self,
        mock_ransom_finding: RansomFinding,
        mock_ransom_stats_healthy: RansomStats,
    ) -> None:
        """Notifier failure → the findings are returned anyway."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)
        client.check_domain = AsyncMock(return_value=[mock_ransom_finding])

        notifier = MagicMock()
        notifier.send_ransom_alert = AsyncMock(side_effect=Exception("SMTP error"))

        tracker = RansomwareTracker(client=client, notifier=notifier)

        # Must not raise an exception même si le notifier échoue
        findings = await tracker.run("mondomaine.fr")
        assert len(findings) == 1


class TestRansomwareTrackerContext:
    """Tests for the get_context() method."""

    @pytest.mark.asyncio
    async def test_get_context_returns_stats(self, mock_ransom_stats_healthy: RansomStats) -> None:
        """get_context() returns the instance stats."""
        client = MagicMock()
        client.check_health = AsyncMock(return_value=mock_ransom_stats_healthy)

        tracker = RansomwareTracker(client=client)
        stats = await tracker.get_context()

        assert stats.is_healthy is True
        assert stats.groups_tracked == 124
