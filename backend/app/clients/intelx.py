"""
breachradar/clients/intelx.py

Client de recherche Intelligence X (IntelX).
"""
from __future__ import annotations

import logging
import asyncio

from app.clients.base import BaseLeakClient
from app.core.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)

class IntelXClient(BaseLeakClient):
    """
    Client pour l'API Intelligence X.
    """
    name = "intelx"
    rate_limit_delay = 2.0

    def __init__(self, api_key: str, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://2.intelx.io"
        self.sanitizer = sanitizer or DataSanitizer()

    async def check_email(self, email: str) -> list[LeakFinding]:
        return await self._search(email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        return await self._search(domain)

    async def _search(self, term: str) -> list[LeakFinding]:
        if not self.api_key:
            return []

        await self._apply_rate_limit()

        headers = {"x-key": self.api_key}
        client = self._build_http_client(headers=headers)
        
        try:
            # 1. Initier la recherche
            payload = {
                "term": term,
                "maxresults": 20,
                "media": 0,
                "sort": 2, # Sort by date
                "terminate": []
            }
            search_resp = await client.post(f"{self.base_url}/intelligent/search", json=payload)
            search_resp.raise_for_status()
            search_data = search_resp.json()
            search_id = search_data.get("id")
            
            if not search_id:
                return []

            # 2. Poller les résultats (On attend 2 secondes pour laisser le temps au backend IntelX)
            await asyncio.sleep(2.0)
            
            result_resp = await client.get(f"{self.base_url}/intelligent/search/result", params={"id": search_id, "limit": 20})
            result_resp.raise_for_status()
            result_data = result_resp.json()
            
            records = result_data.get("records", [])
            
            findings = []
            for record in records:
                finding = self._parse_record(term, record)
                if finding:
                    findings.append(finding)
                    
            return findings

        except Exception as e:
            logger.error(f"[{self.name}] Erreur lors de la requête API: {e}")
            return []
        finally:
            await client.aclose()

    def _parse_record(self, term: str, record: dict) -> LeakFinding | None:
        try:
            name = record.get("name", "IntelX Dump")
            date_str = record.get("date", "")
            bucket = record.get("bucket", "Unknown Bucket")
            
            return LeakFinding(
                source=self.name,
                email=term if "@" in term else f"unknown@{term}",
                breach_name=f"{bucket} - {name}",
                breach_date=None, # On pourrait parser date_str si besoin
                data_classes=["IntelX Record"],
                has_password=False, # Impossible à affirmer sans lire le contenu brut via l'ID
                has_hash=False,
                has_api_key=False,
                severity=Severity.MEDIUM,
                verified=True,
                is_sensitive=False,
            )
        except Exception as e:
            logger.error(f"[{self.name}] Erreur de parsing record : {e}")
            return None
