"""
BreachRadar WebUI — GitHub Webhooks
====================================
Endpoint pour recevoir les alertes GitHub en temps réel
(ex: Secret Scanning Alerts ou Push events).
"""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Header, HTTPException, Request, Response

from app.core.config import settings
from app.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_signature(payload_body: bytes, secret_token: str, signature_header: str) -> bool:
    """Vérifie la signature HMAC de GitHub."""
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: str = Header("ping", alias="X-GitHub-Event"),
) -> Response:
    # Validation du secret (si configuré)
    secret_token = getattr(settings, "github_webhook_secret", None)
    if secret_token:
        body = await request.body()
        if not verify_signature(body, secret_token, x_hub_signature_256):
            logger.warning("[Webhook] Signature GitHub invalide.")
            raise HTTPException(status_code=403, detail="Forbidden: Invalid Signature")

    if x_github_event == "ping":
        return Response(content="Pong")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Bad Request: Invalid JSON")

    # Traitement basique d'une alerte Secret Scanning
    if x_github_event == "secret_scanning_alert":
        action = payload.get("action")
        alert = payload.get("alert", {})
        repo = payload.get("repository", {}).get("full_name", "unknown/repo")

        if action == "created":
            secret_type = alert.get("secret_type", "unknown_secret")
            logger.error(f"[🚨 ALERTE GITHUB] Secret détecté dans {repo} : {secret_type}")

            # Envoi d'une notification via NotificationEngine (ex: Webhook, Email)
            notifier = NotificationEngine(settings)
            message = f"ALERTE GITHUB SECRET SCANNING\nRepo: {repo}\nType: {secret_type}\nURL: {alert.get('html_url')}"

            if settings.ransomlook_alert_webhook:
                await notifier.send_webhook(settings.ransomlook_alert_webhook, message)

    return Response(content="OK")
