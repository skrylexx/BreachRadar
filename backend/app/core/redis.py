"""
BreachRadar WebUI — Redis Client
================================
Redis client for revoked JWT sessions (blacklist) and rate limiting.
"""

import redis.asyncio as aioredis

from app.core.config import settings

# ─── Redis singleton client ───────────────────────────────────────────────────
redis_client: aioredis.Redis = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def blacklist_token(jti: str, expire_seconds: int) -> None:
    """Adds a JTI (JWT ID) to the Redis blacklist during logout."""
    await redis_client.setex(f"blacklist:{jti}", expire_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Checks if a token is revoked (blacklisted)."""
    return await redis_client.exists(f"blacklist:{jti}") > 0


async def store_mfa_challenge(user_id: str, challenge_token: str, expire_seconds: int = 300) -> None:
    """
    Stores a temporary MFA challenge token (5 min).
    Key: mfa_challenge:{token} -> Value: user_id
    """
    await redis_client.setex(f"mfa_challenge:{challenge_token}", expire_seconds, user_id)


async def verify_mfa_challenge(challenge_token: str) -> str | None:
    """
    Verifies and consumes the MFA challenge (single use).
    Returns the user_id if valid, None otherwise.
    """
    res = await redis_client.getdel(f"mfa_challenge:{challenge_token}")
    if res is None:
        return None
    return res.decode("utf-8") if isinstance(res, bytes) else str(res)


# ─── Brute-force protection (MFA) ───────────────────────────────────────────


async def increment_mfa_failures(user_id: str) -> int:
    """Increments the MFA failure counter and returns the new value."""
    key = f"mfa_failures:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 900)  # 15 minutes of blocking
    return count


async def get_mfa_failures(user_id: str) -> int:
    """Retrieves the number of current MFA failures."""
    val = await redis_client.get(f"mfa_failures:{user_id}")
    return int(val) if val else 0


async def reset_mfa_failures(user_id: str) -> None:
    """Resets the MFA failure counter."""
    await redis_client.delete(f"mfa_failures:{user_id}")
