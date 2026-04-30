"""
breachradar/clients/dehashed.py

Client Dehashed API.
"""
from __future__ import annotations

import logging

from breachradar.clients.base import BaseLeakClient
from breachradar.core.sanitizer import DataSanitizer
from breachradar.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)

class DehashedClient(BaseLeakClient):
    """
    Client pour l'API Dehashed.
    """
    name = "dehashed"
    rate_limit_delay = 0.5

    def __init__(self, dehashed_email: str, api_key: str, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.dehashed_email = dehashed_email
        self.api_key = api_key
        self.base_url = "https://api.dehashed.com"
        self.sanitizer = sanitizer or DataSanitizer()

    async def check_email(self, email: str) -> list[LeakFinding]:
        if not self.dehashed_email or not self.api_key:
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/search"
        params = {"query": f'email:"{email}"'}

        client = self._build_http_client()
        client.auth = (self.dehashed_email, self.api_key)

        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if not response:
            return []

        data = response.json()
        if "entries" not in data or not data["entries"]:
            return []

        findings = []
        for entry in data["entries"]:
            if not isinstance(entry, dict):
                continue
            finding = self._parse_entry(email, entry)
            if finding:
                findings.append(finding)

        return findings

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        if not self.dehashed_email or not self.api_key:
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/search"
        params = {"query": f'domain:"{domain}"'}

        client = self._build_http_client()
        client.auth = (self.dehashed_email, self.api_key)

        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if not response:
            return []

        data = response.json()
        if "entries" not in data or not data["entries"]:
            return []

        findings = []
        for entry in data["entries"]:
            if not isinstance(entry, dict):
                continue
            email = entry.get("email")
            if not email:
                email = f"unknown@{domain}"
            finding = self._parse_entry(email, entry)
            if finding:
                findings.append(finding)

        return findings

    def _parse_entry(self, email: str, entry: dict) -> LeakFinding | None:
        sanitized = self.sanitizer.sanitize(entry)
        safe_entry = sanitized.sanitized_data if isinstance(sanitized.sanitized_data, dict) else entry

        try:
            breach_name = safe_entry.get("database_name", "Unknown Dehashed Source")
            password = safe_entry.get("password")
            hashed_password = safe_entry.get("hashed_password")

            has_password = bool(password)
            has_hash = bool(hashed_password)
            
            data_classes = ["Email addresses"]
            if has_password:
                data_classes.append("Passwords")
            if has_hash:
                data_classes.append("Hashed Passwords")
            
            if safe_entry.get("username"):
                data_classes.append("Usernames")

            return LeakFinding(
                source=self.name,
                email=email,
                breach_name=breach_name,
                breach_date=None,
                data_classes=data_classes,
                has_password=has_password,
                has_hash=has_hash,
                has_api_key=False,
                severity=Severity.HIGH if (has_password or has_hash) else Severity.MEDIUM,
                verified=True,
                is_sensitive=True,
            )
        except Exception as e:
            logger.error(f"[{self.name}] Erreur de parsing pour {email}: {e}")
            return None
