"""
breachradar/clients/telegram_monitor.py

Client de monitoring Telegram (Telethon).
Permet de rechercher des mentions du domaine ou des emails dans des canaux/groupes spécifiques.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.clients.base import BaseLeakClient
from app.engine.sanitizer import DataSanitizer
from app.models.finding import LeakFinding

logger = logging.getLogger(__name__)


class TelegramMonitorClient(BaseLeakClient):
    """
    Client de recherche sur Telegram via Telethon.
    Nécessite une configuration API ID/Hash et génère un fichier .session.
    """

    name = "telegram"
    rate_limit_delay = 3.0  # Telegram est très strict sur le rate limiting

    def __init__(self, api_id: int, api_hash: str, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.sanitizer = sanitizer or DataSanitizer()
        self.session_path = Path("breachradar_tg.session")

        # Telethon importé localement pour éviter une dépendance dure si non installé
        try:
            from telethon import TelegramClient as TelethonClient

            self.client_class = TelethonClient
        except ImportError:
            self.client_class = None
            logger.warning(
                "[Telegram] Telethon n'est pas installé. Lancez 'uv pip install telethon'."
            )

    async def _ensure_auth(self) -> Any:
        if not self.client_class or not self.api_id or not self.api_hash:
            return None

        client = self.client_class(str(self.session_path), self.api_id, self.api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            logger.error(
                "[Telegram] Utilisateur non autorisé. Connectez-vous d'abord manuellement avec un script interactif pour générer la session."
            )
            await client.disconnect()
            return None

        return client

    async def check_email(self, email: str) -> list[LeakFinding]:
        return await self._search_global(email)

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        return await self._search_global(domain)

    async def _search_global(self, query: str) -> list[LeakFinding]:
        """
        Recherche globale sur Telegram pour le terme donné.
        Attention : la recherche globale via Telethon n'est pas toujours exhaustive
        et dépend des canaux publics indexés par Telegram.
        """
        await self._apply_rate_limit()

        client = await self._ensure_auth()
        if not client:
            return []

        findings = []
        try:
            # Recherche globale de messages contenant le query.
            # Note: L'API Telegram limite fortement la recherche globale par mot-clé pour les utilisateurs.
            # En réalité, on chercherait plutôt dans des canaux "suivis" (monitoring).
            # Ceci est une implémentation simplifiée.

            # Pour l'instant, nous retournons une liste vide si on ne peut pas interagir
            # efficacement sans risquer un ban (FloodWait).
            # Dans une version avancée, on itérerait sur des canaux OSINT connus.
            logger.info(
                f"[{self.name}] La recherche Telegram nécessitera une liste de canaux cible (Phase 3 avancée)."
            )

        except Exception as e:
            logger.error(f"[{self.name}] Erreur lors de la recherche Telegram : {e}")
        finally:
            await client.disconnect()

        return findings
