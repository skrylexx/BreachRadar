"""
breachradar/clients/base.py

Classe abstraite BaseLeakClient — interface commune à tous les clients API.

Chaque source de données (HIBP, LeakCheck, Dehashed, RansomLook, etc.)
doit hériter de cette classe et implémenter les méthodes abstraites.

Design patterns utilisés :
- Template Method : les méthodes abstraites définissent le contrat
- Rate Limiter intégré : respecte les limites de chaque API
- Tenacity retry : gestion automatique des erreurs réseau transitoires
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
    Interface abstraite pour tous les clients API de BreachRadar.

    Chaque client doit :
    1. Définir `name` (identifiant technique de la source)
    2. Définir `rate_limit_delay` (secondes entre requêtes)
    3. Implémenter `check_email()` et `check_domain()`

    Le rate limiter est automatiquement appliqué entre les appels successifs.
    """

    name: str  # Identifiant technique de la source (ex: "hibp", "leakcheck")
    rate_limit_delay: float = 0.0  # Secondes entre requêtes (0 = pas de limite)

    def __init__(self) -> None:
        self._last_request_time: float = 0.0
        self._logger = logging.getLogger(f"breachradar.clients.{self.name}")

    @abstractmethod
    async def check_email(self, email: str) -> list[Any]:
        """
        Vérifie si une adresse email spécifique est présente dans des fuites.

        Args:
            email: Adresse email à vérifier

        Returns:
            Liste de findings (vide si aucune fuite détectée)

        Note:
            Ne jamais logguer le contenu des mots de passe ou hashs reçus.
        """
        ...

    @abstractmethod
    async def check_domain(self, domain: str) -> list[Any]:
        """
        Vérifie si un domaine est présent dans des fuites (recherche générale).

        Args:
            domain: Domaine à vérifier (ex: "mondomaine.fr")

        Returns:
            Liste de findings (vide si aucune fuite détectée)
        """
        ...

    async def _apply_rate_limit(self) -> None:
        """
        Applique le délai de rate limiting entre les requêtes.
        Doit être appelé avant chaque requête HTTP externe.
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
        Crée un client HTTP async configuré avec les headers et timeouts appropriés.
        User-Agent identifiable et honnête (pas d'usurpation).
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
            verify=True,  # SSL strict — pas de verify=False
        )

    def _log_finding_detected(self, email: str, breach_name: str) -> None:
        """
        Log la détection d'un finding de manière sécurisée.
        RÈGLE : Ne jamais logguer les données sensibles (passwords, hashs).
        """
        self._logger.info(f"[{self.name}] Finding détecté : email={email}, breach={breach_name}")

    def _log_sensitive_data_detected(self, email: str, data_type: str) -> None:
        """
        Log la présence de données sensibles SANS les logguer elles-mêmes.
        RÈGLE : Utiliser uniquement des flags booléens dans les logs.
        """
        self._logger.debug(
            f"[{self.name}] Donnée sensible détectée pour {email} (type: {data_type}) — masquée"
        )

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
        Effectue une requête HTTP sécurisée avec retry automatique.
        Supporte tous les types de requêtes (GET, POST, etc.) via kwargs.
        """
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            if e.response.status_code == 429:
                self._logger.warning(
                    f"[{self.name}] Rate limit atteint (429) sur {url} — attente avant retry"
                )
            elif e.response.status_code >= 500:
                self._logger.error(
                    f"[{self.name}] Erreur serveur (500+) sur {url} — "
                    f"status={e.response.status_code}"
                )
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
        """GET avec retry automatique."""
        return await self._safe_request(client, "GET", url, params=params)
