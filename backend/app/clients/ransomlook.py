"""
breachradar/clients/ransomlook.py

Client HTTP pour l'instance Docker RansomLook locale.

RansomLook agrège les publications des portails d'extorsion ransomware
(sites "Name & Shame") et expose une API REST locale.

Particularités de ce client :
- Pas de rate limit strict (requêtes vers localhost)
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
from app.models.finding import LeakFinding
from app.models.ransom import RansomFinding, RansomStats, RansomStatus

logger = logging.getLogger(__name__)

# Chargement du mapping des noms de groupes depuis group_names.yaml
_GROUP_NAMES_PATH = Path(__file__).parent.parent / "config" / "group_names.yaml"


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
    """
    Client pour l'instance Docker RansomLook.

    Ce client est DISTINCT des autres BaseLeakClient car :
    1. Il retourne des RansomFinding (pas des LeakFinding)
    2. Les données ne sont pas sanitisées (publiques par nature)
    3. La sévérité est toujours CRITICAL
    4. Il supporte la recherche multi-termes avec déduplication

    check_email() retourne [] car RansomLook opère au niveau domaine/organisation,
    pas au niveau email individuel.
    """

    name = "ransomlook"
    rate_limit_delay = 0.5  # Délai minimal entre requêtes locales

    def __init__(self, base_url: str, search_terms: list[str] | None = None) -> None:
        """
        Args:
            base_url: URL de l'instance RansomLook (ex: http://localhost:8888)
            search_terms: Termes de recherche supplémentaires (noms commerciaux, etc.)
        """
        super().__init__()
        self.base_url = base_url.rstrip("/")
        self.search_terms = search_terms or []
        self.timeout = httpx.Timeout(30.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        """
        Requête GET vers l'API RansomLook avec retry automatique.

        Raises:
            httpx.HTTPError: En cas d'erreur HTTP non récupérable
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> RansomStats:
        """
        Vérifie que l'instance RansomLook est opérationnelle.

        Returns:
            RansomStats avec is_healthy=False si l'instance est inaccessible.
        """
        try:
            data = await self._get("/api/v1/stats")
            return RansomStats(
                groups_tracked=data.get("groups", 0),
                total_posts=data.get("posts", 0),
                last_update=data.get("last_update"),
                instance_url=self.base_url,
                is_healthy=True,
            )
        except Exception as e:
            logger.error(f"Instance RansomLook non joignable ({self.base_url}) : {e}")
            return RansomStats(
                groups_tracked=0,
                total_posts=0,
                last_update=None,
                instance_url=self.base_url,
                is_healthy=False,
            )

    async def check_domain(self, domain: str) -> list[RansomFinding]:
        """
        Recherche le domaine ET tous les termes configurés dans les settings.
        Déduplique les résultats par (group_name, victim_name, published_at).

        ⚠️  Si des résultats sont trouvés, une alerte CRITIQUE doit être
        déclenchée par le RansomwareTracker IMMÉDIATEMENT.

        Args:
            domain: Domaine cible (ex: "mondomaine.fr")

        Returns:
            Liste de RansomFinding (vide = domaine non compromis ✅)
        """
        findings: list[RansomFinding] = []
        seen: set[tuple[str, str, str | None]] = set()

        # Rechercher sur le domaine + tous les termes configurés
        all_terms = list({domain, *self.search_terms})

        for term in all_terms:
            await self._apply_rate_limit()
            try:
                results = await self._get("/api/v1/victim", params={"name": term})

                if not isinstance(results, list):
                    logger.warning(
                        f"RansomLook: réponse inattendue pour '{term}' : {type(results)}"
                    )
                    continue

                for item in results:
                    # Déduplication par (groupe, victime, date publication)
                    dedup_key = (
                        str(item.get("group_name", "")),
                        str(item.get("post_title", "")),
                        str(item.get("published", "")),
                    )
                    if dedup_key in seen:
                        logger.debug(
                            f"RansomLook: doublon ignoré pour terme '{term}' "
                            f"(groupe={dedup_key[0]})"
                        )
                        continue
                    seen.add(dedup_key)

                    finding = self._parse_victim_item(item, term)
                    if finding:
                        findings.append(finding)
                        # Log CRITIQUE — sans exposer de données sensibles
                        logger.critical(
                            f"🚨 RANSOMWARE ALERT : domaine '{domain}' détecté sur "
                            f"portail {finding.group_display_name} "
                            f"(terme matché: '{term}', victime: '{finding.victim_name}')"
                        )

            except Exception as e:
                logger.error(f"Erreur RansomLook pour terme '{term}' : {e}")

        return findings

    async def check_email(self, email: str) -> list[LeakFinding]:
        """
        Non applicable pour RansomLook (opère au niveau domaine/organisation).
        Retourne toujours une liste vide.
        """
        return []

    async def get_recent_victims(self, days: int = 7) -> list[dict]:
        """
        Retourne les victimes récentes pour enrichissement de contexte du rapport.

        Args:
            days: Nombre de jours à considérer (défaut: 7)

        Returns:
            Liste de victimes récentes (toutes organisations confondues)
        """
        try:
            return await self._get("/api/v1/recent", params={"days": days})
        except Exception as e:
            logger.error(f"Erreur récupération victimes récentes RansomLook : {e}")
            return []

    def _parse_victim_item(self, item: dict, search_term: str) -> RansomFinding | None:
        """
        Parse un item de l'API RansomLook vers un RansomFinding Pydantic.

        Args:
            item: Dictionnaire brut de l'API
            search_term: Terme de recherche qui a produit ce résultat

        Returns:
            RansomFinding ou None si l'item est invalide
        """
        try:
            group_name = item.get("group_name", "unknown")
            group_display = GROUP_DISPLAY_NAMES.get(
                group_name.lower(),
                group_name.replace("_", " ").replace("-", " ").title(),
            )

            # Déterminer le statut (RansomLook ne le fournit pas toujours explicitement)
            status = RansomStatus.UNKNOWN
            if item.get("published"):
                status = RansomStatus.PUBLISHED
            elif item.get("discovered") or item.get("added"):
                status = RansomStatus.LISTED

            # Date de découverte : préférer "added" puis "discovered"
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
                # L'URL .onion est stockée mais masquée dans les rapports finaux
                portal_url=item.get("post_url"),
                search_term_matched=search_term,
            )
        except Exception as e:
            logger.error(f"Erreur parsing item RansomLook : {e} — item={item!r}")
            return None
