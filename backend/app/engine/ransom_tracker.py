"""
breachradar/core/ransom_tracker.py

Orchestration de la surveillance ransomware via RansomLookClient.

Ce module est distinct du client HTTP (ransomlook.py) qui lui est délégué.
Il gère :
1. La vérification de la santé de l'instance RansomLook
2. L'appel au client pour la recherche multi-termes
3. Le déclenchement de l'alerte IMMÉDIATE à la détection

⚠️  RÈGLE CRITIQUE :
L'alerte ransomware est envoyée AVANT la fin du scan global.
La fenêtre de réaction (5-30 jours) justifie cette priorité absolue.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.models.ransom import RansomFinding, RansomStats

if TYPE_CHECKING:
    from app.clients.ransomlook import RansomLookClient
    from app.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)


class RansomwareTracker:
    """
    Orchestre la surveillance ransomware via RansomLookClient.

    Responsabilités :
    - Vérifier que l'instance RansomLook est opérationnelle avant le scan
    - Déclencher la recherche multi-termes
    - Envoyer une alerte IMMÉDIATE pour chaque RansomFinding détecté
    - Retourner les findings pour intégration dans le rapport final

    Usage :
        tracker = RansomwareTracker(client=ransomlook_client, notifier=notifier)
        findings = await tracker.run(domain="mondomaine.fr")
    """

    def __init__(
        self,
        client: RansomLookClient,
        notifier: NotificationEngine | None = None,
    ) -> None:
        """
        Args:
            client: Instance de RansomLookClient configurée
            notifier: NotificationEngine pour les alertes (optionnel)
        """
        self.client = client
        self.notifier = notifier

    async def run(self, domain: str) -> list[RansomFinding]:
        """
        Exécute la surveillance ransomware pour un domaine.

        Séquence :
        1. Vérifier la santé de l'instance RansomLook
        2. Si non disponible : log d'erreur + retour vide (non bloquant)
        3. Recherche multi-termes via RansomLookClient
        4. Pour chaque finding : alerte IMMÉDIATE (sans attendre la fin du scan)

        Args:
            domain: Domaine cible (ex: "mondomaine.fr")

        Returns:
            Liste de RansomFinding (vide = domaine non compromis ✅)
        """
        # 1. Vérifier la santé de l'instance
        stats = await self.client.check_health()

        if not stats.is_healthy:
            logger.error(
                f"Instance RansomLook non disponible ({stats.instance_url}) — "
                "module ignoré pour ce scan. "
                "Vérifier que 'docker compose up ransomlook-app' est exécuté."
            )
            return []

        logger.info(
            f"RansomLook opérationnel : {stats.groups_tracked} groupes suivis, {stats.total_posts} victimes indexées"
        )

        # 2. Recherche multi-termes
        findings = await self.client.check_domain(domain)

        # 3. Alerte immédiate pour chaque finding
        # ⚠️  Cette étape s'exécute AVANT la fin du scan global
        if findings:
            logger.critical(
                f"🚨 RANSOMWARE DETECTION : {len(findings)} alerte(s) pour '{domain}' — "
                "envoi des notifications d'urgence"
            )
            for finding in findings:
                await self._send_immediate_alert(finding, domain)
        else:
            logger.info(f"✅ RansomLook : domaine '{domain}' non détecté sur les portails ransomware")

        return findings

    async def get_context(self) -> RansomStats:
        """
        Retourne les statistiques de l'instance RansomLook.
        Utilisé par le ReportEngine pour enrichir le rapport.
        """
        return await self.client.check_health()

    async def _send_immediate_alert(self, finding: RansomFinding, domain: str) -> None:
        """
        Envoie une alerte d'urgence immédiate pour un RansomFinding.

        CONTENU DE L'ALERTE (minimal, sans données sensibles) :
        - Groupe ransomware détecté
        - Date de détection
        - Taille revendiquée (si disponible)
        - Actions critiques recommandées

        NE CONTIENT PAS :
        - URL .onion du portail
        - Description complète (peut contenir des PII)

        Args:
            finding: Le RansomFinding détecté
            domain: Le domaine concerné
        """
        if not self.notifier:
            logger.warning(
                "Aucun notifier configuré — alerte ransomware non envoyée. "
                "Configurer RANSOMLOOK_ALERT_EMAIL ou RANSOMLOOK_ALERT_WEBHOOK dans .env"
            )
            return

        try:
            await self.notifier.send_ransom_alert(finding)
            logger.info(f"Alerte ransomware envoyée pour '{domain}' — groupe: {finding.group_display_name}")
        except Exception as e:
            logger.error(f"Échec envoi alerte ransomware pour '{domain}' : {e} — vérifier la configuration du notifier")
