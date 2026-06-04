"""
breachradar/core/ransom_tracker.py

Ransomware monitoring orchestration via RansomLookClient.

This module is separate from the HTTP client (ransomlook.py) delegated to it.
It manages:
1. Checking the health of the RansomLook instance
2. Calling the customer for multi-term search
3. Triggering the IMMEDIATE alert upon detection

⚠️ CRITICAL RULE:
The ransomware alert is sent BEFORE the global scan is completed.
The response window (5-30 days) justifies this absolute priority.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.models.ransom import RansomFinding, RansomStats

if TYPE_CHECKING:
    from app.clients.ransomlook import RansomLookClient
    from app.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)


class RansomwareTracker:
    """
    Orchestrates ransomware monitoring via RansomLookClient.

    Responsibilities:
    - Check that the RansomLook instance is operational before scanning
    - Trigger multi-term search
    - Send an IMMEDIATE alert for each RansomFinding detected
    - Return the findings for integration into the final report

    Usage:
        tracker = RansomwareTracker(client=ransomlook_client, notifier=notifier)
        findings = await tracker.run(domain="mydomain.fr")
    """

    def __init__(
        self,
        client: RansomLookClient,
        notifier: NotificationEngine | None = None,
    ) -> None:
        """
        Args:
            client: RansomLookClient instance configured
            notify: NotificationEngine for alerts (optional)
        """
        self.client = client
        self.notifier = notifier

    async def run(self, domain: str) -> list[RansomFinding]:
        """
        Runs ransomware monitoring for a domain.

        Sequence:
        1. Check the health of the RansomLook instance
        2. If not available: error log + empty return (non-blocking)
        3. Multi-term search via RansomLookClient
        4. For each finding: IMMEDIATE alert (without waiting for the end of the scan)

        Args:
            domain: Target domain (eg: "mydomain.fr")

        Returns:
            RansomFinding list (empty = uncompromised domain ✅)
        """
        # 1. Check the health of the instance
        stats = await self.client.check_health()

        if not stats.is_healthy:
            logger.error(
                f"Instance RansomLook non disponible ({stats.instance_url}) — "
                "module ignoré pour ce scan. "
                "Vérifier que 'docker compose up ransomlook-app' est exécuté."
            )
            return []

        logger.info(
            f"RansomLook opérationnel : {stats.groups_tracked} groupes suivis, {stats.total_posts} victimes indexées"
        )

        # 2. Multi-term search
        findings = await self.client.check_domain(domain)

        # 3. Immediate alert for each finding
        # ⚠️ This step is executed BEFORE the end of the global scan
        if findings:
            logger.critical(
                f"🚨 RANSOMWARE DETECTION : {len(findings)} alerte(s) pour '{domain}' — "
                "envoi des notifications d'urgence"
            )
            for finding in findings:
                await self._send_immediate_alert(finding, domain)
        else:
            logger.info(f"✅ RansomLook : domaine '{domain}' non détecté sur les portails ransomware")

        return findings

    async def get_context(self) -> RansomStats:
        """
        Returns the RansomLook instance statistics.
        Used by the ReportEngine to enrich the report.
        """
        return await self.client.check_health()

    async def _send_immediate_alert(self, finding: RansomFinding, domain: str) -> None:
        """
        Sends an immediate emergency alert for a RansomFinding.

        ALERT CONTENT (minimal, without sensitive data):
        - Ransomware group detected
        - Detection date
        - Claimed size (if available)
        - Recommended critical actions

        DOES NOT CONTAIN:
        - .onion URL of the portal
        - Full description (may contain PII)

        Args:
            finding: RansomFinding detected
            domain: The domain concerned
        """
        if not self.notifier:
            logger.warning(
                "Aucun notifier configuré — alerte ransomware non envoyée. "
                "Configurer RANSOMLOOK_ALERT_EMAIL ou RANSOMLOOK_ALERT_WEBHOOK dans .env"
            )
            return

        try:
            await self.notifier.send_ransom_alert(finding)
            logger.info(f"Alerte ransomware envoyée pour '{domain}' — groupe: {finding.group_display_name}")
        except Exception as e:
            logger.error(f"Échec envoi alerte ransomware pour '{domain}' : {e} — vérifier la configuration du notifier")
