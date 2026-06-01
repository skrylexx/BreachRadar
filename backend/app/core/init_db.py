"""
BreachRadar WebUI — Initialisation de la base de données
=========================================================
Crée l'administrateur initial au premier démarrage si aucun utilisateur n'existe.
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.redis import redis_client
from app.core.security import hash_password
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def initialize_database() -> None:
    """
    Initialise la DB au démarrage :
    - Synchronise le schéma (avec verrou Redis pour éviter les race conditions entre workers).
    - Crée l'admin initial si aucun utilisateur n'existe.
    """
    lock_key = "breachradar:db_init_lock"
    # Tenter de prendre le verrou pendant 30 secondes
    is_locked = await redis_client.set(lock_key, "1", nx=True, ex=30)

    if not is_locked:
        logger.debug("Database initialization already in progress by another worker. Waiting...")
        # Attendre un peu que l'autre worker termine
        await asyncio.sleep(2)
        return

    try:
        # 1. Synchronisation du schéma
        # NOTE: SQLAlchemy create_all peut encore lever IntegrityError sur les Enums 
        # en cas de concurrence extrême ou de cleanup incomplet.
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.debug(f"Types already created: {e}")
            else:
                raise

        # 2. Création admin initial
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).limit(1))
            existing_user = result.scalar_one_or_none()

            if existing_user is None:
                logger.info("No users found. Creating initial admin account...")
                admin = User(
                    email=settings.initial_admin_email,
                    hashed_password=hash_password(settings.initial_admin_password),
                    role=UserRole.ADMIN,
                    is_active=True,
                    mfa_enabled=False,
                )
                session.add(admin)
                await session.commit()
                logger.info(f"Initial admin created: {settings.initial_admin_email}")
            else:
                logger.debug("Database already initialized.")
    finally:
        # Libérer le verrou
        await redis_client.delete(lock_key)
