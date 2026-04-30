"""
leakmonitor/clients/leakcheck.py

Client LeakCheck.io API v2.
"""
from __future__ import annotations

import logging

from leakmonitor.clients.base import BaseLeakClient
from leakmonitor.core.sanitizer import DataSanitizer
from leakmonitor.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)

class LeakCheckClient(BaseLeakClient):
    """
    Client pour l'API LeakCheck.io.
    """
    name = "leakcheck"
    rate_limit_delay = 1.0

    def __init__(self, api_key: str, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://leakcheck.io/api/v2"
        self.sanitizer = sanitizer or DataSanitizer()

    async def check_email(self, email: str) -> list[LeakFinding]:
        if not self.api_key:
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/query/{email}"
        headers = {"X-API-Key": self.api_key}
        params = {"type": "email"}

        client = self._build_http_client(headers=headers)
        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if not response:
            return []

        data = response.json()
        if not data.get("success"):
            logger.error(f"[{self.name}] Erreur de l'API pour {email}: {data.get('error')}")
            return []

        results = data.get("result", [])
        findings = []

        for item in results:
            finding = self._parse_result(email, item)
            if finding:
                findings.append(finding)

        return findings

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        if not self.api_key:
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/query/{domain}"
        headers = {"X-API-Key": self.api_key}
        params = {"type": "domain"}

        client = self._build_http_client(headers=headers)
        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if not response:
            return []

        data = response.json()
        if not data.get("success"):
            logger.error(f"[{self.name}] Erreur de l'API pour {domain}: {data.get('error')}")
            return []

        results = data.get("result", [])
        findings = []

        for item in results:
            email_field = item.get("line", "")
            # Extrait l'email si format "email:password"
            email = email_field.split(":")[0] if ":" in email_field else email_field
            if "@" not in email:
                email = f"unknown@{domain}"
            finding = self._parse_result(email, item)
            if finding:
                findings.append(finding)

        return findings

    def _parse_result(self, email: str, item: dict) -> LeakFinding | None:
        sanitized = self.sanitizer.sanitize(item)
        safe_item = sanitized.sanitized_data if isinstance(sanitized.sanitized_data, dict) else item

        try:
            breach_sources = safe_item.get("sources", [])
            if not breach_sources:
                breach_sources = [safe_item.get("source", "Unknown LeakCheck Breach")]
            breach_name = ", ".join(breach_sources)

            # LeakCheck peut retourner un mot de passe en clair dans `line`
            has_password = "password" in safe_item or ":" in safe_item.get("line", "")
            
            # Sévérité
            severity = Severity.HIGH if has_password else Severity.MEDIUM

            return LeakFinding(
                source=self.name,
                email=email,
                breach_name=breach_name,
                breach_date=None,
                data_classes=["Passwords"] if has_password else ["Email addresses"],
                has_password=has_password,
                has_hash=False,
                has_api_key=False,
                severity=severity,
                verified=True,
                is_sensitive=True,
            )
        except Exception as e:
            logger.error(f"[{self.name}] Erreur de parsing pour {email}: {e}")
            return None
