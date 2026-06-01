"""
breachradar/core/orchestrator.py

Orchestrateur central — lance les scans en parallèle sur toutes les sources.
Utilise asyncio.gather() pour optimiser le temps d'exécution.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from app.clients.base import BaseLeakClient
from app.clients.dehashed import DehashedClient
from app.clients.github_monitor import GitHubClient
from app.clients.hibp import HIBPClient
from app.clients.leakcheck import LeakCheckClient
from app.core.config import Settings
from app.core.source_registry import SourceRegistry
from app.engine.sanitizer import DataSanitizer

if TYPE_CHECKING:
    from app.models.finding import LeakFinding

logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """
    Chef d'orchestre : gère l'exécution parallèle des clients API.
    """

    def __init__(
        self, settings: Settings, registry: SourceRegistry, api_keys: dict[str, str] | None = None
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.api_keys = api_keys or {}
        self.sanitizer = DataSanitizer()
        self.clients: list[BaseLeakClient] = self._initialize_clients()

    def _initialize_clients(self) -> list[BaseLeakClient]:
        """Initialise uniquement les clients marqués comme disponibles dans le registre."""
        active_sources = self.registry.active_sources
        clients: list[BaseLeakClient] = []

        # Helper pour récupérer une clé (Priorité DB/Argument > Settings)
        def _get_key(service: str, settings_val: str) -> str:
            return self.api_keys.get(service) or settings_val

        if "hibp" in active_sources:
            clients.append(
                HIBPClient(
                    api_key=_get_key("hibp", self.settings.hibp_api_key),
                    sanitizer=self.sanitizer,
                    rate_limit_delay=self.settings.hibp_rate_limit_ms / 1000.0,
                )
            )

        if "github" in active_sources:
            clients.append(
                GitHubClient(
                    token=_get_key("github", self.settings.github_token), sanitizer=self.sanitizer
                )
            )

        if "leakcheck" in active_sources:
            clients.append(
                LeakCheckClient(
                    api_key=_get_key("leakcheck", self.settings.leakcheck_api_key),
                    sanitizer=self.sanitizer,
                )
            )

        if "dehashed" in active_sources:
            clients.append(
                DehashedClient(
                    dehashed_email=_get_key("dehashed_email", self.settings.dehashed_email),
                    api_key=_get_key("dehashed", self.settings.dehashed_api_key),
                    sanitizer=self.sanitizer,
                )
            )

        if "intelx" in active_sources:
            from app.clients.intelx import IntelXClient

            clients.append(
                IntelXClient(
                    api_key=_get_key("intelx", self.settings.intelx_api_key),
                    sanitizer=self.sanitizer,
                )
            )

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

        logger.info(
            f"Démarrage du scan email pour {len(emails)} adresse(s) sur {len(self.clients)} source(s)."
        )
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

    async def _run_client_for_emails(
        self, client: BaseLeakClient, emails: list[str]
    ) -> list[LeakFinding]:
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

        logger.info(
            f"Démarrage du scan de domaine pour '{domain}' sur {len(self.clients)} source(s)."
        )
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
