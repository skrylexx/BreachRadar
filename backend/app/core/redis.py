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


async def store_mfa_challenge(
    user_id: str, challenge_token: str, expire_seconds: int = 300
) -> None:
    """
    Stocke un token de challenge MFA temporaire (5 min).
    Clé : mfa_challenge:{token} -> Valeur : user_id
    """
    await redis_client.setex(f"mfa_challenge:{challenge_token}", expire_seconds, user_id)


async def verify_mfa_challenge(challenge_token: str) -> str | None:
    """
    Vérifie et consomme le challenge MFA (usage unique).
    Retourne le user_id si valide, None sinon.
    """
    return await redis_client.getdel(f"mfa_challenge:{challenge_token}")


# ─── Brute-force protection (MFA) ───────────────────────────────────────────


async def increment_mfa_failures(user_id: str) -> int:
    """Incrémente le compteur d'échecs MFA et retourne la nouvelle valeur."""
    key = f"mfa_failures:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 900)  # 15 minutes de blocage
    return count


async def get_mfa_failures(user_id: str) -> int:
    """Récupère le nombre d'échecs MFA actuels."""
    val = await redis_client.get(f"mfa_failures:{user_id}")
    return int(val) if val else 0


async def reset_mfa_failures(user_id: str) -> None:
    """Réinitialise le compteur d'échecs MFA."""
    await redis_client.delete(f"mfa_failures:{user_id}")
