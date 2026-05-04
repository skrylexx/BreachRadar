"""
BreachRadar WebUI — Redis Client
================================
Client Redis pour les sessions JWT révoquées (blacklist) et le rate limiting.
"""

import redis.asyncio as aioredis
from app.core.config import settings

# ─── Client Redis singleton ───────────────────────────────────────────────────
redis_client: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def blacklist_token(jti: str, expire_seconds: int) -> None:
    """Ajoute un JTI (JWT ID) à la blacklist Redis lors du logout."""
    await redis_client.setex(f"blacklist:{jti}", expire_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Vérifie si un token est révoqué (blacklisted)."""
    return await redis_client.exists(f"blacklist:{jti}") > 0


async def store_mfa_challenge(user_id: str, challenge_token: str, expire_seconds: int = 300) -> None:
    """
    Stocke un token de challenge MFA temporaire (5 min).
    Utilisé entre la validation password et la validation TOTP.
    """
    await redis_client.setex(f"mfa_challenge:{user_id}", expire_seconds, challenge_token)


async def verify_mfa_challenge(user_id: str, challenge_token: str) -> bool:
    """Vérifie et consomme le challenge MFA (usage unique)."""
    stored = await redis_client.getdel(f"mfa_challenge:{user_id}")
    return stored == challenge_token
