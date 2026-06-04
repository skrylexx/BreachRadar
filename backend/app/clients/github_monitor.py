"""
breachradar/clients/github_monitor.py

GitHub Monitor client.

Search for hardcoded credentials or domain/email mentions
in the public GitHub repositories.

Special features:
- Rate limit of 60 req/h without token, 5000 req/h with token
- Search code via GitHub Search API
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)


class GitHubClient(BaseLeakClient):
    """
    Client for GitHub Search API.
    """

    name = "github"
    rate_limit_delay = 2.0  # 2 seconds by default to respect the secondary rate limit of the search API

    def __init__(self, token: str = "", sanitizer: DataSanitizer | None = None) -> None:
        """
        Args:
            token: Personal Access Token GitHub (optional)
            sanitizer: DataSanitizer (optional, but recommended)
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
        Checks if an email address is mentioned in code files
        on GitHub, potentially next to passwords.
        """
        # Limit to the first 10 results to avoid too many false positives and preserve the rate limit
        return await self._search_code(query=f'"{email}"', context=email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        """
        Checks if the domain is mentioned with sensitive keywords.
        """
        # Targeted search for potential secrets (limited by GitHub search syntax)
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

            # Ideally, the contents of the file should be retrieved to verify
            # if it actually contains a secret. To avoid exhausting the rate limit,
            # the presence of the domain/email is reported in a suspicious context.

            finding = LeakFinding(
                source=self.name,
                email=context if "@" in context else "N/A (Domain Match)",
                breach_name=f"GitHub Public Repo ({repo_name})",
                breach_date=datetime.now(UTC).date(),
                data_classes=["Source Code", "Potential Credentials"],
                severity=Severity.MEDIUM,  # Medium severity because they are potential false positives
                verified=False,
            )
            findings.append(finding)

        return findings
