"""
breachradar/clients/hibp.py

Client HaveIBeenPwned (HIBP).

Particularités de ce client :
- Rate limit strict de 1500ms entre chaque requête
- Nécessite une clé API (hibp-api-key)
- Permet la recherche par email
- Inclut la vérification k-anonymity des mots de passe (SHA-1)
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
    Client pour HaveIBeenPwned API v3.
    """

    name = "hibp"

    def __init__(
        self, api_key: str, sanitizer: DataSanitizer | None = None, rate_limit_delay: float = 1.5
    ) -> None:
        """
        Args:
            api_key: Clé API HaveIBeenPwned
            sanitizer: DataSanitizer (optionnel, mais recommandé)
            rate_limit_delay: Délai en secondes entre requêtes (défaut: 1.5)
        """
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.sanitizer = sanitizer or DataSanitizer()
        self.rate_limit_delay = rate_limit_delay

    async def check_email(self, email: str) -> list[LeakFinding]:
        """
        Vérifie si une adresse email a été compromise selon HIBP.

        Args:
            email: L'adresse email à vérifier

        Returns:
            Liste des LeakFinding correspondant aux breaches
        """
        if not self.api_key:
            logger.warning("HIBPClient utilisé sans clé API, requête ignorée.")
            return []

        await self._apply_rate_limit()

        url = f"{self.base_url}/breachedaccount/{email}"
        headers = {
            "hibp-api-key": self.api_key,
        }

        # Demander tous les détails (truncateResponse=false)
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
        La recherche par domaine sur HIBP nécessite un abonnement spécial (Domain Search).
        Cette méthode retourne une liste vide dans l'implémentation standard.
        """
        logger.info(
            "La recherche de domaine HIBP requiert l'abonnement Domain Search. Utilisez check_email pour chaque adresse email résolue."
        )
        return []

    async def check_password(self, password: str) -> int:
        """
        Vérifie si un mot de passe a été fuité, via le modèle k-anonymity (Pwned Passwords).
        Envoie uniquement les 5 premiers caractères du hash SHA-1.
        Ne nécessite PAS de clé API, rate limit différent (non appliqué ici, mais attention).

        Args:
            password: Le mot de passe en clair (sera haché localement)

        Returns:
            Le nombre de fois où le mot de passe a été vu dans les fuites (0 = safe)
        """
        # Hachage SHA-1 local (RÈGLE DE SÉCURITÉ : on n'envoie JAMAIS le mot de passe)
        # HIBP k-anonymity REQUIERT SHA-1.
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()  # nosec # nosemgrep
        prefix = sha1[:5]
        suffix = sha1[5:]

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        # Ce service ne requiert pas de clé API et autorise plus de requêtes
        client = httpx.AsyncClient(headers={"User-Agent": "BreachRadar/0.1.0"})

        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Erreur lors de la vérification PwnedPasswords: {e}")
            await client.aclose()
            return 0

        await client.aclose()

        # La réponse contient des lignes 'SUFFIX:COUNT'
        lines = response.text.splitlines()
        for line in lines:
            if line.startswith(f"{suffix}:"):
                count_str = line.split(":")[1]
                return int(count_str)

        return 0

    def _parse_breach(self, email: str, breach: dict) -> LeakFinding | None:
        """Parse un dictionnaire breach de HIBP vers LeakFinding."""
        # Sanitize data before parsing (just in case)
        sanitized = self.sanitizer.sanitize(breach)
        safe_breach = (
            sanitized.sanitized_data if isinstance(sanitized.sanitized_data, dict) else breach
        )

        try:
            breach_date_str = safe_breach.get("BreachDate")
            breach_date = None
            if breach_date_str:
                with contextlib.suppress(ValueError):
                    breach_date = datetime.strptime(breach_date_str, "%Y-%m-%d").date()

            data_classes = safe_breach.get("DataClasses", [])
            data_classes_lower = [d.lower() for d in data_classes]

            # Déduire les types de données exposées
            has_password = "passwords" in data_classes_lower
            has_hash = False  # HIBP ne dit pas toujours si le mdp est hashé, mais en général "passwords" couvre les deux.

            # Si un mot de passe est exposé, on le marque (l'aggregator gérera la sévérité).
            # On suppose que ce ne sont pas des credentials en clair sauf si c'est spécifié autrement.

            is_sensitive = safe_breach.get("IsSensitive", False)
            is_verified = safe_breach.get("IsVerified", True)

            # Sévérité par défaut, l'aggregator recalculera
            severity = Severity.HIGH if has_password else Severity.MEDIUM

            return LeakFinding(
                source=self.name,
                email=email,
                breach_name=safe_breach.get("Name", "Unknown"),
                breach_date=breach_date,
                data_classes=data_classes,
                has_password=has_password,
                has_hash=has_hash,
                has_api_key=False,  # HIBP ne précise pas souvent "API keys" dans data classes de la même manière
                severity=severity,
                verified=is_verified,
                is_sensitive=is_sensitive,
            )
        except Exception as e:
            logger.error(f"Erreur de parsing HIBP breach pour {email}: {e}")
            return None
