"""
leakmonitor/clients/pastebin_monitor.py

Client de monitoring pour Pastebin (via un service OSINT public ou scrapé).
"""
from __future__ import annotations

import logging

from leakmonitor.clients.base import BaseLeakClient
from leakmonitor.core.sanitizer import DataSanitizer
from leakmonitor.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)

class PastebinClient(BaseLeakClient):
    """
    Client de recherche sur Pastebin.
    En l'absence d'accès à la Scraping API officielle de Pastebin,
    ce client peut s'appuyer sur des APIs OSINT tierces ou agir comme stub
    jusqu'à configuration d'un compte Pro Pastebin ou IntelX.
    """
    name = "pastebin"
    rate_limit_delay = 2.0

    def __init__(self, api_key: str | None = None, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_key = api_key
        # psbdmp.ws est un index non-officiel très utilisé en OSINT pour Pastebin
        self.base_url = "https://psbdmp.ws/api/search"
        self.sanitizer = sanitizer or DataSanitizer()

    async def check_email(self, email: str) -> list[LeakFinding]:
        # psbdmp recherche globale
        return await self._search(email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        return await self._search(domain)

    async def _search(self, query: str) -> list[LeakFinding]:
        await self._apply_rate_limit()

        url = f"{self.base_url}/{query}"

        client = self._build_http_client()
        try:
            # PsbDmp API retourne { "data": [ {"id": "xxx", "tags": [], "time": "..."} ] }
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
        # On limite le nombre de findings pour ne pas noyer le rapport
        # Souvent une recherche domaine remonte beaucoup de faux positifs
        for item in results[:15]:
            paste_id = item.get("id")
            if not paste_id:
                continue
                
            paste_url = f"https://pastebin.com/{paste_id}"
            
            finding = LeakFinding(
                source=self.name,
                email=query if "@" in query else f"unknown@{query}",
                breach_name=f"Pastebin Dump ({paste_id})",
                breach_date=None,
                data_classes=["Paste/Dump Text"],
                has_password=False, # Impossible de savoir sans télécharger et analyser le texte brut
                has_hash=False,
                has_api_key=False,
                severity=Severity.MEDIUM, # Sévérité modérée pour un dump brut, nécessite investigation manuelle
                verified=False,
                is_sensitive=False, # Le texte brut n'est pas téléchargé ici pour des raisons de perf/privacy
            )
            findings.append(finding)

        return findings
