"""
breachradar/clients/pastebin_monitor.py

Monitoring client for Pastebin (via a public or scraped OSINT service).
"""

from __future__ import annotations

import logging

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)


class PastebinClient(BaseLeakClient):
    """
    Search client on Pastebin.
    In the absence of access to the official Pastebin Scraping API,
    this client can rely on third-party OSINT APIs or act as a stub
    until you configure a Pro Pastebin or IntelX account.
    """

    name = "pastebin"
    rate_limit_delay = 2.0

    def __init__(self, api_key: str | None = None, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_key = api_key
        # psbdmp.ws is an unofficial index widely used in OSINT for Pastebin
        self.base_url = "https://psbdmp.ws/api/search"
        self.sanitizer = sanitizer or DataSanitizer()

    async def check_email(self, email: str) -> list[LeakFinding]:
        # psbdmp global search
        return await self._search(email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        return await self._search(domain)

    async def _search(self, query: str) -> list[LeakFinding]:
        await self._apply_rate_limit()

        url = f"{self.base_url}/{query}"

        client = self._build_http_client()
        try:
            # PsbDmp API returns { "data": [ {"id": "xxx", "tags": [], "time": "..."} ] }
            response = await self._safe_get(client, url)
        finally:
            await client.aclose()

        if not response:
            return []

        try:
            data = response.json()
        except ValueError:
            return []

        results = data.get("data", [])
        if not results:
            return []

        findings = []
        # We limit the number of findings so as not to drown out the report
        # Often a domain search brings up a lot of false positives
        for item in results[:15]:
            paste_id = item.get("id")
            if not paste_id:
                continue

            finding = LeakFinding(
                source=self.name,
                email=query if "@" in query else f"unknown@{query}",
                breach_name=f"Pastebin Dump ({paste_id})",
                breach_date=None,
                data_classes=["Paste/Dump Text"],
                has_password=False,  # Impossible to know without downloading and analyzing the raw text
                has_hash=False,
                has_api_key=False,
                severity=Severity.MEDIUM,  # Moderate severity for a raw dump, requires manual investigation
                verified=False,
                is_sensitive=False,  # Plain text is not uploaded here for perf/privacy reasons
            )
            findings.append(finding)

        return findings
