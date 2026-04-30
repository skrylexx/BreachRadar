"""
breachradar/clients/github_webhook.py

Serveur webhook léger (aiohttp) pour recevoir les alertes GitHub en temps réel
(ex: Secret Scanning Alerts ou Push events).
"""
import logging
from aiohttp import web
import hmac
import hashlib

from breachradar.config.settings import get_settings
from breachradar.models.finding import LeakFinding, Severity
from breachradar.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

def verify_signature(payload_body: bytes, secret_token: str, signature_header: str) -> bool:
    """Vérifie la signature HMAC de GitHub."""
    if not signature_header:
        return False
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@routes.post('/webhook/github')
async def handle_github_webhook(request: web.Request) -> web.Response:
    settings = get_settings()
    
    # Validation du secret (si configuré)
    secret_token = getattr(settings, "github_webhook_secret", None)
    if secret_token:
        signature = request.headers.get('X-Hub-Signature-256', '')
        body = await request.read()
        if not verify_signature(body, secret_token, signature):
            logger.warning("[Webhook] Signature GitHub invalide.")
            return web.Response(status=403, text="Forbidden: Invalid Signature")

    event = request.headers.get('X-GitHub-Event', 'ping')
    
    if event == "ping":
        return web.Response(text="Pong")
        
    try:
        payload = await request.json()
    except Exception:
        return web.Response(status=400, text="Bad Request: Invalid JSON")

    # Traitement basique d'une alerte Secret Scanning
    if event == "secret_scanning_alert":
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

    return web.Response(text="OK")

async def start_webhook_server(port: int = 8080):
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Serveur Webhook GitHub démarré sur le port {port}")
    return runner
