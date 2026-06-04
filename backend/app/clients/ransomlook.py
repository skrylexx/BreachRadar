"""
breachradar/clients/ransomlook.py

HTTP client for the RansomLook instance (local or SaaS).

- In "local" mode, we query the Docker instance (internal HTTP, no API key)
- In "saas" mode, we query https://www.ransomlook.io/api with a header
  Authorization: <API_KEY>

Special features of this client:
- No strict rate limit (reasonable local or SaaS requests)
- Multi-term search with deduplication
- Immediate CRITICAL alert upon detection (without waiting for the end of the scan)
- Data is PUBLIC (published by ransomware groups)
  → No sanitization necessary

API used:
    GET /api/v1/stats → Instance health
    GET /api/v1/victim?name=X → Search by victim name/domain
    GET /api/v1/recent?days=N → Recent kills (context)
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

from app.clients.base import BaseLeakClient
from app.core.config import settings
from app.models.finding import LeakFinding
from app.models.ransom import RansomFinding, RansomStats, RansomStatus

logger = logging.getLogger(__name__)

# Loading group name mapping from group_names.yaml
_GROUP_NAMES_PATH = Path(__file__).parent.parent / "core" / "group_names.yaml"


def _load_group_names() -> dict[str, str]:
    """Loads the technical mapping → displayable from group_names.yaml."""
    try:
        with _GROUP_NAMES_PATH.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("group_names", {})
    except FileNotFoundError:
        logger.warning("group_names.yaml introuvable — utilisation du .title() par défaut")
        return {}


GROUP_DISPLAY_NAMES: dict[str, str] = _load_group_names()


class RansomLookClient(BaseLeakClient):
    """Client for the RansomLook API (local or SaaS).

    This client is DISTINCT from other BaseLeakClients because:
    1. It returns RansomFinding (not LeakFinding)
    2. The data is not sanitized (public by nature)
    3. Severity is always CRITICAL
    4. It supports multi-term search with deduplication

    check_email() returns [] because RansomLook operates at the domain/organization level,
    not at the individual email level.
    """

    name = "ransomlook"
    rate_limit_delay = 0.5  # Minimum delay between requests

    def __init__(
        self,
        mode: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        super().__init__()

        self.mode = mode or settings.ransomlook_mode

        if self.mode == "local":
            self.base_url = base_url or settings.ransomlook_local_url.rstrip("/")
            self.headers: dict[str, str] = {}
        else:  # saas
            self.base_url = base_url or settings.ransomlook_saas_api_url.rstrip("/")
            key = api_key or settings.ransomlook_saas_api_key
            if not key:
                raise RuntimeError("RANSOMLOOK_SAAS_API_KEY est requis lorsque RANSOMLOOK_MODE=saas")
            self.headers = {
                "Authorization": key,
            }

        self.search_terms = settings.all_ransomlook_terms
        self.timeout = httpx.Timeout(settings.request_timeout_seconds)

        logger.info("RansomLookClient initialisé en mode %s sur %s", self.mode, self.base_url)

    async def _fetch_local_key(self) -> str | None:
        """Retrieves the auto-generated API key from the local instance."""
        if self.mode != "local":
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/key")
                if response.status_code == 200:
                    key = response.json().get("api_key")
                    if key:
                        logger.info("Clé API RansomLook locale récupérée avec succès.")
                        self.headers = {"Authorization": key}
                        return key
        except Exception as e:
            logger.debug("Impossible de récupérer la clé RansomLook locale : %s", e)
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        """GET request to RansomLook API with automatic retry."""
        # If we are local and do not yet have a key, we try to recover it
        if self.mode == "local" and not self.headers.get("Authorization"):
            await self._fetch_local_key()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> RansomStats:
        """Verifies that the RansomLook instance is operational."""
        path = "/api/v1/stats" if self.mode == "saas" else "/api/stats"
        try:
            data = await self._get(path)
            if not isinstance(data, dict):
                raise ValueError("RansomLook API returned unexpected format")
            return RansomStats(
                groups_tracked=data.get("groups", 0),
                total_posts=data.get("posts", 0),
                last_update=data.get("last_update"),
                instance_url=self.base_url,
                mode=self.mode,
                is_healthy=True,
            )
        except Exception as e:
            logger.error(
                "Instance RansomLook non joignable (%s, mode=%s) : %s",
                self.base_url,
                self.mode,
                e,
            )
            return RansomStats(
                groups_tracked=0,
                total_posts=0,
                last_update=None,
                instance_url=self.base_url,
                is_healthy=False,
            )

    async def check_domain(self, domain: str) -> list[RansomFinding]:
        """Searches the domain AND all the terms configured in the settings.

        Deduplicates results by (group_name, victim_name, published_at).
        ⚠️ If results are found, a CRITICAL alert should be
        triggered by the RansomwareTracker IMMEDIATELY.
        """
        findings: list[RansomFinding] = []
        seen: set[tuple[str, str, str | None]] = set()

        all_terms = list({domain, *self.search_terms})
        path = "/api/v1/victim" if self.mode == "saas" else "/api/victim"

        for term in all_terms:
            await self._apply_rate_limit()
            try:
                results = await self._get(path, params={"name": term})

                if not isinstance(results, list):
                    logger.warning("RansomLook: réponse inattendue pour '%s' : %s", term, type(results))
                    continue

                for item in results:
                    dedup_key = (
                        str(item.get("group_name", "")),
                        str(item.get("post_title", "")),
                        str(item.get("published", "")),
                    )
                    if dedup_key in seen:
                        logger.debug(
                            "RansomLook: doublon ignoré pour terme '%s' (groupe=%s)",
                            term,
                            dedup_key[0],
                        )
                        continue
                    seen.add(dedup_key)

                    finding = self._parse_victim_item(item, term)
                    if finding:
                        findings.append(finding)
                        logger.critical(
                            "🚨 RANSOMWARE ALERT : domaine '%s' détecté sur portail %s "
                            "(terme matché: '%s', victime: '%s')",
                            domain,
                            finding.group_display_name,
                            term,
                            finding.victim_name,
                        )

            except Exception as e:
                logger.error("Erreur RansomLook pour terme '%s' : %s", term, e)

        return findings

    async def check_email(self, email: str) -> list[LeakFinding]:
        """Not applicable for RansomLook (domain/organization level)."""
        return []

    async def get_recent_victims(self, days: int = 7) -> list[dict]:
        """Returns recent victims for context enrichment."""
        path = "/api/v1/recent" if self.mode == "saas" else "/api/recent"
        try:
            # Note: Local API doesn't support 'days' param yet, it returns last 100
            params = {"days": days} if self.mode == "saas" else {}
            res = await self._get(path, params=params)
            from typing import cast

            return cast(list[dict], res)
        except Exception as e:
            logger.error("Erreur récupération victimes récentes RansomLook : %s", e)
            return []

    def _parse_victim_item(self, item: dict, search_term: str) -> RansomFinding | None:
        """Parses an item from the RansomLook API to a Pydantic RansomFinding."""
        try:
            group_name = item.get("group_name", "unknown")
            group_display = GROUP_DISPLAY_NAMES.get(
                group_name.lower(),
                group_name.replace("_", " ").replace("-", " ").title(),
            )

            status = RansomStatus.UNKNOWN
            if item.get("published"):
                status = RansomStatus.PUBLISHED
            elif item.get("discovered") or item.get("added"):
                status = RansomStatus.LISTED

            from datetime import UTC, datetime

            discovered_at_str = item.get("added") or item.get("discovered")
            if discovered_at_str:
                try:
                    discovered_at = datetime.fromisoformat(str(discovered_at_str).replace("Z", "+00:00"))
                except ValueError:
                    discovered_at = datetime.now(UTC)
            else:
                discovered_at = datetime.now(UTC)

            return RansomFinding(
                group_name=group_name,
                group_display_name=group_display,
                victim_name=item.get("post_title", ""),
                victim_website=item.get("website"),
                discovered_at=discovered_at,
                published_at=item.get("published"),
                description=item.get("description"),
                country=item.get("country"),
                activity=item.get("activity"),
                claim_size=item.get("claim_size"),
                status=status,
                portal_url=item.get("post_url"),
                search_term_matched=search_term,
            )
        except Exception as e:
            logger.error("Erreur parsing item RansomLook : %s — item=%r", e, item)
            return None
