"""
leakmonitor/core/orchestrator.py

Orchestrateur central — lance les scans en parallèle sur toutes les sources.
Utilise asyncio.gather() pour optimiser le temps d'exécution.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from leakmonitor.clients.base import BaseLeakClient
from leakmonitor.clients.github_monitor import GitHubClient
from leakmonitor.clients.hibp import HIBPClient
from leakmonitor.config.settings import Settings
from leakmonitor.config.source_registry import SourceRegistry
from leakmonitor.core.sanitizer import DataSanitizer

if TYPE_CHECKING:
    from leakmonitor.models.finding import LeakFinding

logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """
    Chef d'orchestre : gère l'exécution parallèle des clients API.
    """

    def __init__(self, settings: Settings, registry: SourceRegistry) -> None:
        self.settings = settings
        self.registry = registry
        self.sanitizer = DataSanitizer()
        self.clients: list[BaseLeakClient] = self._initialize_clients()

    def _initialize_clients(self) -> list[BaseLeakClient]:
        """Initialise uniquement les clients marqués comme disponibles dans le registre."""
        active_sources = self.registry.active_sources
        clients: list[BaseLeakClient] = []

        if "hibp" in active_sources:
            clients.append(HIBPClient(api_key=self.settings.hibp_api_key, sanitizer=self.sanitizer))

        if "github" in active_sources:
            clients.append(GitHubClient(token=self.settings.github_token, sanitizer=self.sanitizer))

        # Ajouter ici les autres clients (LeakCheck, Dehashed, etc.)

        return clients

    async def scan_emails(self, emails: list[str]) -> list[LeakFinding]:
        """
        Lance la recherche pour une liste d'emails en parallèle sur tous les clients.
        Attention: Pour les API comme HIBP qui ont un rate limit par requête, 
        l'exécution par client doit se faire email par email de façon séquentielle 
        à l'intérieur du client, ou le client lui-même gère le rate_limit via son delay.
        """
        if not emails or not self.clients:
            return []

        logger.info(f"Démarrage du scan email pour {len(emails)} adresse(s) sur {len(self.clients)} source(s).")
        all_findings: list[LeakFinding] = []

        # Pour chaque client, on traite la liste des emails
        tasks = []
        for client in self.clients:
            tasks.append(self._run_client_for_emails(client, emails))

        # asyncio.gather lance les clients en parallèle (HIBP et GitHub tournent en même temps)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erreur inattendue dans un client lors du scan: {result}")
            elif isinstance(result, list):
                all_findings.extend(result)

        return all_findings

    async def _run_client_for_emails(self, client: BaseLeakClient, emails: list[str]) -> list[LeakFinding]:
        """Exécute un client donné pour tous les emails de manière séquentielle (pour respecter son propre rate_limit)."""
        findings = []
        for email in emails:
            try:
                result = await client.check_email(email)
                if result:
                    findings.extend(result)
            except Exception as e:
                logger.error(f"[{client.name}] Échec lors du scan de {email}: {e}")
        return findings

    async def scan_domain(self, domain: str) -> list[LeakFinding]:
        """
        Lance la recherche de domaine en parallèle sur tous les clients.
        """
        if not self.clients:
            return []

        logger.info(f"Démarrage du scan de domaine pour '{domain}' sur {len(self.clients)} source(s).")
        all_findings: list[LeakFinding] = []

        tasks = []
        for client in self.clients:
            tasks.append(self._run_client_domain(client, domain))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erreur inattendue dans un client lors du scan domaine: {result}")
            elif isinstance(result, list):
                all_findings.extend(result)

        return all_findings

    async def _run_client_domain(self, client: BaseLeakClient, domain: str) -> list[LeakFinding]:
        try:
            return await client.check_domain(domain)
        except Exception as e:
            logger.error(f"[{client.name}] Échec lors du scan de domaine {domain}: {e}")
            return []
