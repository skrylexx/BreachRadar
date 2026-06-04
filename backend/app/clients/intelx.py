"""
breachradar/clients/intelx.py

Intelligence X (IntelX) Research Client.
"""

from __future__ import annotations

import asyncio
import logging

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)


class IntelXClient(BaseLeakClient):
    """
    Client for the Intelligence X API.
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
            # 1. Initiate the search
            payload = {
                "term": term,
                "maxresults": 20,
                "media": 0,
                "sort": 2,  # Sort by date
                "terminate": [],
            }
            search_resp = await self._safe_request(client, "POST", f"{self.base_url}/intelligent/search", json=payload)
            if not search_resp:
                return []

            search_data = search_resp.json()
            search_id = search_data.get("id")

            if not search_id:
                return []

            # 2. Poll the results (We wait 2 seconds to give the IntelX backend time)
            await asyncio.sleep(2.0)

            result_resp = await self._safe_request(
                client,
                "GET",
                f"{self.base_url}/intelligent/search/result",
                params={"id": search_id, "limit": 20},
            )
            if not result_resp:
                return []

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
            record.get("date", "")
            bucket = record.get("bucket", "Unknown Bucket")

            return LeakFinding(
                source=self.name,
                email=term if "@" in term else f"unknown@{term}",
                breach_name=f"{bucket} - {name}",
                breach_date=None,  # We could parse date_str if necessary
                data_classes=["IntelX Record"],
                has_password=False,  # Impossible to assert without reading raw content via ID
                has_hash=False,
                has_api_key=False,
                severity=Severity.MEDIUM,
                verified=True,
                is_sensitive=False,
            )
        except Exception as e:
            logger.error(f"[{self.name}] Erreur de parsing record : {e}")
            return None
