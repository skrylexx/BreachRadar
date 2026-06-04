"""
breachradar/clients/hibp.py

Customer HaveIBeenPwned (HIBP).

Special features of this client:
- Strict rate limit of 1500ms between each request
- Requires an API key (hibp-api-key)
- Allows searching by email
- Includes k-anonymity password verification (SHA-1)
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
from datetime import datetime

import httpx

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding, Severity

logger = logging.getLogger(__name__)


class HIBPClient(BaseLeakClient):
    """
    Client for HaveIBeenPwned API v3.
    """

    name = "hibp"

    def __init__(self, api_key: str, sanitizer: DataSanitizer | None = None, rate_limit_delay: float = 1.5) -> None:
        """
        Args:
            api_key: HaveIBeenPwned API key
            sanitizer: DataSanitizer (optional, but recommended)
            rate_limit_delay: Delay in seconds between requests (default: 1.5)
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.sanitizer = sanitizer or DataSanitizer()
        self.rate_limit_delay = rate_limit_delay

    async def check_email(self, email: str) -> list[LeakFinding]:
        """
        Checks if an email address has been compromised according to HIBP.

        Args:
            email: The email address to check

        Returns:
            List of LeakFindings corresponding to breaches
        """
        if not self.api_key:
            logger.warning("HIBPClient utilisé sans clé API, requête ignorée.")
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/breachedaccount/{email}"
        headers = {
            "hibp-api-key": self.api_key,
        }

        # Request full details (truncateResponse=false)
        params = {"truncateResponse": "false"}

        client = self._build_http_client(headers=headers)

        try:
            response = await self._safe_get(client, url, params=params)
        finally:
            await client.aclose()

        if response is None:
            # 404 = clean
            return []

        breaches = response.json()
        findings = []

        for breach in breaches:
            finding = self._parse_breach(email, breach)
            if finding:
                findings.append(finding)

        return findings

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        """
        Domain search on HIBP requires a special subscription (Domain Search).
        This method returns an empty list in the standard implementation.
        """
        logger.info(
            "La recherche de domaine HIBP requiert l'abonnement Domain Search. Utilisez check_email pour chaque adresse email résolue."
        )
        return []

    async def check_password(self, password: str) -> int:
        """
        Checks if a password has been leaked, via the k-anonymity model (Pwned Passwords).
        Sends only the first 5 characters of the SHA-1 hash.
        Does NOT require an API key, different rate limit (not applied here, but be careful).

        Args:
            password: The plaintext password (will be hashed locally)

        Returns:
            The number of times the password was seen in leaks (0 = safe)
        """
        # Local SHA-1 hash (SECURITY RULE: NEVER send the password)
        # HIBP k-anonymity REQUIRES SHA-1.
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()  # nosec # nosemgrep
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        # This service does not require an API key and allows more requests
        client = httpx.AsyncClient(headers={"User-Agent": "BreachRadar/0.1.0"})

        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Erreur lors de la vérification PwnedPasswords: {e}")
            await client.aclose()
            return 0

        await client.aclose()

        # Response contains 'SUFFIX:COUNT' lines
        lines = response.text.splitlines()
        for line in lines:
            if line.startswith(f"{suffix}:"):
                count_str = line.split(":")[1]
                return int(count_str)

        return 0

    def _parse_breach(self, email: str, breach: dict) -> LeakFinding | None:
        """Parses a breach dictionary from HIBP to LeakFinding."""
        # Sanitize data before parsing (just in case)
        sanitized = self.sanitizer.sanitize(breach)
        safe_breach = sanitized.sanitized_data if isinstance(sanitized.sanitized_data, dict) else breach

        try:
            breach_date_str = safe_breach.get("BreachDate")
            breach_date = None
            if breach_date_str:
                with contextlib.suppress(ValueError):
                    breach_date = datetime.strptime(breach_date_str, "%Y-%m-%d").date()

            data_classes = safe_breach.get("DataClasses", [])
            data_classes_lower = [d.lower() for d in data_classes]

            # Infer the types of data exposed
            has_password = "passwords" in data_classes_lower
            has_hash = (
                False  # HIBP doesn't always say whether the password is hashed, but generally "passwords" covers both.
            )

            # If a password is exposed, we mark it (the aggregator will manage the severity).
            # It is assumed that these are not plaintext credentials unless otherwise specified.

            is_sensitive = safe_breach.get("IsSensitive", False)
            is_verified = safe_breach.get("IsVerified", True)

            # Default severity, the aggregator will recalculate
            severity = Severity.HIGH if has_password else Severity.MEDIUM

            return LeakFinding(
                source=self.name,
                email=email,
                breach_name=safe_breach.get("Name", "Unknown"),
                breach_date=breach_date,
                data_classes=data_classes,
                has_password=has_password,
                has_hash=has_hash,
                has_api_key=False,  # HIBP does not often specify "API keys" in data classes in the same way
                severity=severity,
                verified=is_verified,
                is_sensitive=is_sensitive,
            )
        except Exception as e:
            logger.error(f"Erreur de parsing HIBP breach pour {email}: {e}")
            return None
