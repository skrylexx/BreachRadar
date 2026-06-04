"""
breachradar/clients/telegram_monitor.py

Telegram monitoring client (Telethon).
Allows you to search for mentions of the domain or emails in specific channels/groups.
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
    Search client on Telegram via Telethon.
    Requires ID/Hash API configuration and generates a .session file.
    """

    name = "telegram"
    rate_limit_delay = 3.0  # Telegram is very strict on rate limiting

    def __init__(self, api_id: int, api_hash: str, sanitizer: DataSanitizer | None = None) -> None:
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.sanitizer = sanitizer or DataSanitizer()
        self.session_path = Path("breachradar_tg.session")

        # Telethon imported locally to avoid hard dependency if not installed
        try:
            from telethon import TelegramClient as TelethonClient

            self.client_class = TelethonClient
        except ImportError:
            self.client_class = None
            logger.warning("[Telegram] Telethon n'est pas installé. Lancez 'uv pip install telethon'.")

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
        Global search on Telegram for the given term.
        Please note: the global search via Telethon is not always exhaustive
        and depends on public channels indexed by Telegram.
        """
        await self._apply_rate_limit()

        client = await self._ensure_auth()
        if not client:
            return []

        findings: list[LeakFinding] = []
        try:
            # Global search for messages containing the query.
            # Note: The Telegram API heavily limits global keyword search for users.
            # In reality, we would rather look in “monitoring” channels.
            # This is a simplified implementation.

            # For now, we return an empty list if we cannot interact
            # effectively without risking a ban (FloodWait).
            # In an advanced version, we would iterate over known OSINT channels.
            logger.info(f"[{self.name}] La recherche Telegram nécessitera une liste de canaux cible (Phase 3 avancée).")

        except Exception as e:
            logger.error(f"[{self.name}] Erreur lors de la recherche Telegram : {e}")
        finally:
            await client.disconnect()

        return findings
