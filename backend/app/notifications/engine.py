"""
breachradar/notifications/engine.py

Moteur de notifications (Email, Webhook).
Gère l'envoi des alertes critiques (Ransomware) de manière asynchrone.
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader

from app.core.config import Settings
from app.models.ransom import RansomFinding

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "report" / "templates"


class NotificationEngine:
    """
    Gère l'envoi d'alertes via les canaux configurés.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    async def send_ransom_alert(self, finding: RansomFinding) -> None:
        """
        Envoie une alerte ransomware sur tous les canaux configurés.
        """
        if not self.settings.ransomlook_alert_configured:
            logger.warning("Aucun canal d'alerte configuré pour les alertes RansomLook.")
            return

        # Rendre le template de notification
        try:
            template = self.env.get_template("notification.txt.j2")
            message = template.render(
                domain=self.settings.target_domain,
                alert=finding
            )
        except Exception as e:
            logger.error(f"Erreur de rendu du template d'alerte: {e}")
            message = f"ALERTE CRITIQUE: Le domaine a été détecté sur le portail de {finding.group_display_name}."

        # Envoi via Webhook
        if self.settings.ransomlook_alert_webhook:
            await self.send_webhook(self.settings.ransomlook_alert_webhook, message)

        # Envoi via Email (Stub pour l'instant - implémentation SMTP à faire)
        if self.settings.ransomlook_alert_email:
            await self.send_email(self.settings.ransomlook_alert_email, "ALERTE CRITIQUE RANSOMWARE", message)

    async def send_webhook(self, url: str, message: str) -> None:
        """Envoie une notification via Webhook (Discord, Slack, etc.)."""
        payload = {"text": message, "content": message} # format compatible Slack et Discord
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            logger.info(f"Alerte webhook envoyée avec succès à {url}")
        except Exception as e:
            logger.error(f"Échec de l'envoi du webhook: {e}")

    async def send_email(self, to_address: str, subject: str, message: str) -> None:
        """Envoi d'email SMTP de manière asynchrone."""
        if not self.settings.smtp_server or not self.settings.smtp_username:
            logger.warning("Configuration SMTP manquante, impossible d'envoyer l'email.")
            return
            
        import smtplib
        from email.message import EmailMessage
        import asyncio
        
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = self.settings.smtp_from or self.settings.smtp_username
        msg["To"] = to_address

        def _send():
            try:
                server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port, timeout=10)
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Alerte email envoyée avec succès à {to_address}")
            except Exception as e:
                logger.error(f"Échec de l'envoi d'email SMTP: {e}")

        await asyncio.to_thread(_send)
