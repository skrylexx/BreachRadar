"""
breachradar/resolver/email_resolver.py

Email address resolver.
For Phase 1, we use a static list or common addresses.
Integration with tools like Hunter.io or theHarvester is planned for Phase 2.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailResolver:
    """
    Resolves email addresses associated with a domain.
    Uses Hunter.io (if API configured), theHarvester (if installed), and a local/common list.
    """

    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.settings = get_settings()
        self.common_prefixes = ["admin", "contact", "info", "support", "webmaster", "security"]

    async def resolve(self) -> list[str]:
        """
        Returns a list of email addresses to scan for the domain.
        Combination of:
        - Common prefixes
        - emails.txt
        - Hunter.io (if key configured)
        - theHarvester (via subprocess)
        """
        emails: set[str] = set()

        # 1. Common addresses
        for prefix in self.common_prefixes:
            emails.add(f"{prefix}@{self.domain}")

        # 2. Local file
        emails_file = Path("emails.txt")
        if emails_file.exists():
            try:
                with emails_file.open(encoding="utf-8") as f:
                    for line in f:
                        email = line.strip().lower()
                        if email and email.endswith(f"@{self.domain}"):
                            emails.add(email)
                logger.info(f"[Resolver] {len(emails) - len(self.common_prefixes)} emails chargés depuis emails.txt")
            except Exception as e:
                logger.error(f"[Resolver] Erreur lecture {emails_file}: {e}")

        # 3. Hunter.io
        if self.settings.hunter_configured:
            hunter_emails = await self._run_hunter()
            emails.update(hunter_emails)

        # 4. theHarvester
        harvester_emails = await self._run_theharvester()
        emails.update(harvester_emails)

        resolved = sorted(emails)
        logger.info(f"[Resolver] Total : {len(resolved)} adresses email uniques trouvées pour {self.domain}")
        return resolved

    async def _run_hunter(self) -> list[str]:
        logger.info(f"[Resolver] Interrogation de Hunter.io pour {self.domain}")
        url = "https://api.hunter.io/v2/domain-search"
        params: dict[str, Any] = {
            "domain": self.domain,
            "api_key": self.settings.hunter_api_key,
            "limit": 100,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                emails_data = data.get("data", {}).get("emails", [])
                found = [e.get("value").lower() for e in emails_data if e.get("value")]
                logger.info(f"[Resolver] Hunter.io: {len(found)} emails trouvés")
                return found
            except Exception as e:
                logger.error(f"[Resolver] Erreur Hunter.io : {e}")
                return []

    async def _run_theharvester(self) -> list[str]:
        logger.info(f"[Resolver] Lancement de theHarvester pour {self.domain}")
        found: list[str] = []
        try:
            # We execute asynchronously so as not to block
            process = await asyncio.create_subprocess_exec(
                "theHarvester",
                "-d",
                self.domain,
                "-b",
                "duckduckgo,yahoo",
                "-l",
                "100",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                output = stdout.decode("utf-8", errors="ignore")
                # rudimentary email parsing in theHarvester output
                in_emails_section = False
                for line in output.splitlines():
                    line = line.strip()
                    if "Emails found:" in line or "[+] Emails found:" in line:
                        in_emails_section = True
                        continue
                    if in_emails_section:
                        if not line or "[" in line or "Hosts found" in line:
                            in_emails_section = False
                            continue
                        if f"@{self.domain}" in line.lower():
                            found.append(line.lower())
                logger.info(f"[Resolver] theHarvester: {len(found)} emails trouvés")
            else:
                logger.warning(f"[Resolver] theHarvester a retourné le code {process.returncode}. (Non installé ?)")
        except FileNotFoundError:
            logger.warning("[Resolver] theHarvester n'est pas installé ou n'est pas dans le PATH.")
        except Exception as e:
            logger.error(f"[Resolver] Erreur theHarvester : {e}")

        return found
