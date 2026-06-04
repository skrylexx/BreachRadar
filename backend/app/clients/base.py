"""
breachradar/clients/base.py

Abstract class BaseLeakClient — interface common to all API clients.

Each data source (HIBP, LeakCheck, Dehashed, RansomLook, etc.)
must inherit from this class and implement the abstract methods.

Design patterns used:
- Template Method: abstract methods define the contract
- Integrated Rate Limiter: respects the limits of each API
- Tenacity retry: automatic management of transient network errors
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.finding import LeakFinding

logger = logging.getLogger(__name__)


class BaseLeakClient(ABC):
    """
    Abstract interface for all BreachRadar API clients.

    Each customer must:
    1. Define `name` (technical identifier of the source)
    2. Set `rate_limit_delay` (seconds between requests)
    3. Implement `check_email()` and `check_domain()`

    The rate limiter is automatically applied between successive calls.
    """

    name: str  # Technical identifier of the source (e.g. "hibp", "leakcheck")
    rate_limit_delay: float = 0.0  # Seconds between requests (0 = no limit)

    def __init__(self) -> None:
        self._last_request_time: float = 0.0
        self._logger = logging.getLogger(f"breachradar.clients.{self.name}")

    @abstractmethod
    async def check_email(self, email: str) -> list[Any]:
        """
        Checks if a specific email address is present in leaks.

        Args:
            email: Email address to check

        Returns:
            List of findings (empty if no leak detected)

        Note:
            Never log the content of passwords or hashes received.
        """
        ...

    @abstractmethod
    async def check_domain(self, domain: str) -> list[Any]:
        """
        Checks if a domain is present in leaks (general search).

        Args:
            domain: Domain to check (ex: "mondomaine.fr")

        Returns:
            List of findings (empty if no leak detected)
        """
        ...

    async def _apply_rate_limit(self) -> None:
        """
        Applies rate limiting delay between requests.
        Must be called before each external HTTP request.
        """
        if self.rate_limit_delay <= 0:
            return

        elapsed = time.monotonic() - self._last_request_time
        wait_time = self.rate_limit_delay - elapsed

        if wait_time > 0:
            self._logger.debug(f"Rate limit [{self.name}] : attente {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        self._last_request_time = time.monotonic()

    def _build_http_client(
        self,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> httpx.AsyncClient:
        """
        Creates an async HTTP client configured with the appropriate headers and timeouts.
        Identifiable and honest User-Agent (no spoofing).
        """
        default_headers = {
            "User-Agent": "BreachRadar/0.1.0 (OSINT defensif - usage legitime)",
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)

        return httpx.AsyncClient(
            headers=default_headers,
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            verify=True,  # Strict SSL — no verify=False
        )

    def _log_finding_detected(self, email: str, breach_name: str) -> None:
        """
        Log the detection of a finding in a secure manner.
        RULE: Never log sensitive data (passwords, hashes).
        """
        self._logger.info(f"[{self.name}] Finding détecté : email={email}, breach={breach_name}")

    def _log_sensitive_data_detected(self, email: str, data_type: str) -> None:
        """
        Log the presence of sensitive data WITHOUT logging them themselves.
        RULE: Use only Boolean flags in logs.
        """
        self._logger.debug(f"[{self.name}] Donnée sensible détectée pour {email} (type: {data_type}) — masquée")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=False,
    )
    async def _safe_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response | None:
        """
        Makes a secure HTTP request with automatic retry.
        Supports all types of requests (GET, POST, etc.) via kwargs.
        """
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            if e.response.status_code == 429:
                self._logger.warning(f"[{self.name}] Rate limit atteint (429) sur {url} — attente avant retry")
            elif e.response.status_code >= 500:
                self._logger.error(f"[{self.name}] Erreur serveur (500+) sur {url} — status={e.response.status_code}")
            raise
        except httpx.RequestError as e:
            self._logger.error(f"[{self.name}] Erreur réseau sur {url} : {e}")
            raise

    async def _safe_get(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response | None:
        """GET with automatic retry."""
        return await self._safe_request(client, "GET", url, params=params)
