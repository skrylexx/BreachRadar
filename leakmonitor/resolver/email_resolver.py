"""
leakmonitor/resolver/email_resolver.py

Résolveur d'adresses email.
Pour la Phase 1, on utilise une liste statique ou des adresses communes.
L'intégration avec des outils comme Hunter.io ou theHarvester est prévue pour la Phase 2.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailResolver:
    """
    Résout les adresses email associées à un domaine.
    """

    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.common_prefixes = ["admin", "contact", "info", "support", "webmaster", "security"]

    async def resolve(self) -> list[str]:
        """
        Retourne une liste d'adresses email à scanner pour le domaine.
        Dans cette version basique, on génère les adresses communes et on cherche 
        un fichier local `emails.txt`.
        """
        emails = set()

        # 1. Adresses communes
        for prefix in self.common_prefixes:
            emails.add(f"{prefix}@{self.domain}")

        # 2. Lecture fichier local (si existant)
        emails_file = Path("emails.txt")
        if emails_file.exists():
            try:
                with emails_file.open(encoding="utf-8") as f:
                    for line in f:
                        email = line.strip().lower()
                        if email and email.endswith(f"@{self.domain}"):
                            emails.add(email)
                logger.info(f"Chargement de {len(emails) - len(self.common_prefixes)} emails depuis {emails_file}")
            except Exception as e:
                logger.error(f"Erreur lors de la lecture de {emails_file}: {e}")

        resolved = sorted(list(emails))
        logger.info(f"Résolveur: {len(resolved)} adresses email trouvées pour {self.domain}")
        return resolved
