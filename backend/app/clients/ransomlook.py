"""
breachradar/clients/ransomlook.py

Client HTTP pour l'instance RansomLook (locale ou SaaS).

- En mode "local", on interroge l'instance Docker (HTTP interne, pas d'API key)
- En mode "saas", on interroge https://www.ransomlook.io/api avec un header
  Authorization: <API_KEY>

Particularités de ce client :
- Pas de rate limit strict (requêtes locales ou SaaS raisonnables)
- Recherche multi-termes avec déduplication
- Alerte CRITIQUE immédiate à la détection (sans attendre la fin du scan)
- Les données sont PUBLIQUES (publiées par les groupes ransomware)
  → Pas de sanitisation nécessaire

API utilisée :
    GET /api/v1/stats            → Santé de l'instance
    GET /api/v1/victim?name=X    → Recherche par nom de victime/domaine
    GET /api/v1/recent?days=N    → Victimes récentes (contexte)
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

# Chargement du mapping des noms de groupes depuis group_names.yaml
_GROUP_NAMES_PATH = Path(__file__).parent.parent / "core" / "group_names.yaml"


def _load_group_names() -> dict[str, str]:
    """Charge le mapping technique → affichable depuis group_names.yaml."""
    try:
        with _GROUP_NAMES_PATH.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("group_names", {})
    except FileNotFoundError:
        logger.warning("group_names.yaml introuvable — utilisation du .title() par défaut")
        return {}


GROUP_DISPLAY_NAMES: dict[str, str] = _load_group_names()


class RansomLookClient(BaseLeakClient):
    """Client pour l'API RansomLook (locale ou SaaS).

    Ce client est DISTINCT des autres BaseLeakClient car :
    1. Il retourne des RansomFinding (pas des LeakFinding)
    2. Les données ne sont pas sanitisées (publiques par nature)
    3. La sévérité est toujours CRITICAL
    4. Il supporte la recherche multi-termes avec déduplication

    check_email() retourne [] car RansomLook opère au niveau domaine/organisation,
    pas au niveau email individuel.
    """

    name = "ransomlook"
    rate_limit_delay = 0.5  # Délai minimal entre requêtes

    def __init__(self) -> None:
        super().__init__()

        self.mode = settings.ransomlook_mode

        if self.mode == "local":
            self.base_url = settings.ransomlook_local_url.rstrip("/")
            self.headers: dict[str, str] = {}
        else:  # saas
            self.base_url = settings.ransomlook_saas_api_url.rstrip("/")
            if not settings.ransomlook_saas_api_key:
                raise RuntimeError(
                    "RANSOMLOOK_SAAS_API_KEY est requis lorsque RANSOMLOOK_MODE=saas"
                )
            self.headers = {
                "Authorization": settings.ransomlook_saas_api_key,
            }

        self.search_terms = settings.all_ransomlook_terms
        self.timeout = httpx.Timeout(settings.request_timeout_seconds)

        logger.info(
            "RansomLookClient initialisé en mode %s sur %s", self.mode, self.base_url
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        """Requête GET vers l'API RansomLook avec retry automatique."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> RansomStats:
        """Vérifie que l'instance RansomLook est opérationnelle."""
        path = "/api/v1/stats" if self.mode == "saas" else "/api/stats"
        try:
            data = await self._get(path)
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
        """Recherche le domaine ET tous les termes configurés dans les settings.

        Déduplique les résultats par (group_name, victim_name, published_at).
        ⚠️  Si des résultats sont trouvés, une alerte CRITIQUE doit être
        déclenchée par le RansomwareTracker IMMÉDIATEMENT.
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
                    logger.warning(
                        "RansomLook: réponse inattendue pour '%s' : %s", term, type(results)
                    )
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
        """Non applicable pour RansomLook (niveau domaine/organisation)."""
        return []

    async def get_recent_victims(self, days: int = 7) -> list[dict]:
        """Retourne les victimes récentes pour enrichissement de contexte."""
        path = "/api/v1/recent" if self.mode == "saas" else "/api/recent"
        try:
            # Note: Local API doesn't support 'days' param yet, it returns last 100
            params = {"days": days} if self.mode == "saas" else {}
            return await self._get(path, params=params)
        except Exception as e:
            logger.error("Erreur récupération victimes récentes RansomLook : %s", e)
            return []

    def _parse_victim_item(self, item: dict, search_term: str) -> RansomFinding | None:
        """Parse un item de l'API RansomLook vers un RansomFinding Pydantic."""
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

            discovered_at = item.get("added") or item.get("discovered")
            if not discovered_at:
                from datetime import datetime

                discovered_at = datetime.utcnow().isoformat()

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
