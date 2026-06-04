"""
breachradar/notifications/engine.py

Notification engine (Email, Webhook).
Manages the sending of critical alerts (Ransomware) asynchronously.
"""

from __future__ import annotations

import logging
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import Settings
from app.models.finding import CyberFinding
from app.models.ransom import RansomFinding

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "report" / "templates"


class NotificationEngine:
    """
    Manages sending alerts through configured channels.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.env = Environment(  # nosemgrep
            loader=FileSystemLoader(str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(["html", "xml", "txt"]),
        )

    async def send_ransom_alert(self, finding: RansomFinding) -> None:
        """
        Sends a ransomware alert to all configured channels.
        """
        if not self.settings.ransomlook_alert_configured:
            logger.warning("Aucun canal d'alerte configuré pour les alertes RansomLook.")
            return

        # Render the notification template
        try:
            template = self.env.get_template("notification.txt.j2")
            message = template.render(domain=self.settings.target_domain, alert=finding)
        except Exception as e:
            logger.error(f"Erreur de rendu du template d'alerte: {e}")
            message = f"ALERTE CRITIQUE: Le domaine a été détecté sur le portail de {finding.group_display_name}."

        # Sending via Webhook
        if self.settings.ransomlook_alert_webhook:
            await self.send_webhook(self.settings.ransomlook_alert_webhook, message)

        # Sending via Email (Stub for now - SMTP implementation to be done)
        if self.settings.ransomlook_alert_email:
            await self.send_email(self.settings.ransomlook_alert_email, "ALERTE CRITIQUE RANSOMWARE", message)

    async def send_intel_alert(self, finding: CyberFinding) -> None:
        """
        Sends a critical cyber alert.
        """
        if not self.settings.ransomlook_alert_configured:  # We are reusing the same channels for now
            return

        message = (
            f"⚠️ ALERTE VEILLE CYBER - {finding.severity.value}\n"
            f"Source: {finding.source}\n"
            f"Type: {finding.finding_type}\n"
            f"Titre: {finding.title}\n"
            f"Description: {finding.description[:200] if finding.description else 'N/A'}...\n"
            f"Lien: {finding.url or 'N/A'}"
        )

        if self.settings.ransomlook_alert_webhook:
            await self.send_webhook(self.settings.ransomlook_alert_webhook, message)

        if self.settings.ransomlook_alert_email:
            await self.send_email(
                self.settings.ransomlook_alert_email,
                f"ALERTE VEILLE: {finding.title[:50]}",
                message,
            )

    async def send_webhook(self, url: str, message: str) -> None:
        """Sends a notification via Webhook (Discord, Slack, etc.)."""
        payload = {"text": message, "content": message}  # Slack and Discord compatible format

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            logger.info(f"Alerte webhook envoyée avec succès à {url}")
        except Exception as e:
            logger.error(f"Échec de l'envoi du webhook: {e}")

    async def send_email(self, to_address: str, subject: str, message: str) -> None:
        """Sending SMTP email asynchronously."""
        if not self.settings.smtp_host or not self.settings.smtp_user:
            logger.warning("Configuration SMTP manquante, impossible d'envoyer l'email.")
            return

        import asyncio
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = self.settings.smtp_from_email or self.settings.smtp_user
        msg["To"] = to_address

        def _send():
            try:
                server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10)
                if self.settings.smtp_tls:
                    server.starttls()
                server.login(self.settings.smtp_user, self.settings.smtp_password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Alerte email envoyée avec succès à {to_address}")
            except Exception as e:
                logger.error(f"Échec de l'envoi d'email SMTP: {e}")

        await asyncio.to_thread(_send)
