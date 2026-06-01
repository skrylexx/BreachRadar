"""
breachradar/clients/github_monitor.py

Client GitHub Monitor.

Recherche de credentials hardcodés ou de mentions du domaine/email
dans les dépôts publics GitHub.

Particularités:
- Rate limit de 60 req/h sans token, 5000 req/h avec token
- Recherche de code via l'API GitHub Search
"""

from __future__ import annotations

import logging
from datetime import datetime

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)


class GitHubClient(BaseLeakClient):
    """
    Client pour GitHub Search API.
    """

    name = "github"
    rate_limit_delay = 2.0  # 2 secondes par défaut pour respecter le secondary rate limit de l'API search

    def __init__(self, token: str = "", sanitizer: DataSanitizer | None = None) -> None:
        """
        Args:
            token: Personal Access Token GitHub (optionnel)
            sanitizer: DataSanitizer (optionnel, mais recommandé)
        """
        super().__init__()
        self.token = token
        self.base_url = "https://api.github.com"
        self.sanitizer = sanitizer or DataSanitizer()

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    async def check_email(self, email: str) -> list[LeakFinding]:
        """
        Vérifie si une adresse email est mentionnée dans des fichiers de code
        sur GitHub, potentiellement à côté de mots de passe.
        """
        # Limiter aux 10 premiers résultats pour éviter trop de faux positifs et préserver le rate limit
        return await self._search_code(query=f'"{email}"', context=email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        """
        Vérifie si le domaine est mentionné avec des mots-clés sensibles.
        """
        # Recherche ciblée sur des secrets potentiels (limité par la syntaxe de recherche GitHub)
        query = f'"{domain}" AND (password OR secret OR token OR credentials)'
        return await self._search_code(query=query, context=domain)

    async def _search_code(self, query: str, context: str) -> list[LeakFinding]:
        await self._apply_rate_limit()

        url = f"{self.base_url}/search/code"
        params = {
            "q": query,
            "per_page": 10,
        }

        client = self._build_http_client(headers=self._get_headers())

        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if response is None:
            return []

        data = response.json()
        items = data.get("items", [])

        findings = []
        for item in items:
            repo_name = item.get("repository", {}).get("full_name", "Unknown Repo")
            item.get("path", "Unknown File")
            item.get("html_url", "")

            # Dans l'idéal, il faudrait récupérer le contenu du fichier pour vérifier
            # s'il contient réellement un secret. Pour ne pas épuiser le rate limit,
            # on signale la présence du domaine/email dans un contexte suspect.

            finding = LeakFinding(
                source=self.name,
                email=context if "@" in context else "N/A (Domain Match)",
                breach_name=f"GitHub Public Repo ({repo_name})",
                breach_date=datetime.utcnow().date(),
                data_classes=["Source Code", "Potential Credentials"],
                severity=Severity.MEDIUM,  # Sévérité moyenne car ce sont des faux positifs potentiels
                verified=False,
            )
            findings.append(finding)

        return findings
