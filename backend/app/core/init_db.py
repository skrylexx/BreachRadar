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
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        # Tenter de prendre le verrou pendant 60 secondes
        is_locked = await redis_client.set(lock_key, "1", nx=True, ex=60)

        if is_locked:
            break
        
        logger.debug("Database initialization already in progress by another worker. Waiting...")
        await asyncio.sleep(2)
        retry_count += 1
    
    if retry_count >= max_retries:
        logger.warning("Could not acquire DB init lock after several attempts. Proceeding with caution.")

    try:
        # 1. Synchronisation du schéma
        async with engine.begin() as conn:
            # On utilise run_sync pour appeler create_all qui est synchrone dans SQLAlchemy
            await conn.run_sync(Base.metadata.create_all)
        
        # 2. Création admin initial
        async with AsyncSessionLocal() as session:
            # Vérifier si l'admin existe déjà (par email)
            result = await session.execute(select(User).where(User.email == settings.initial_admin_email))
            existing_admin = result.scalar_one_or_none()

            if existing_admin is None:
                # Vérifier si un autre utilisateur existe quand même
                res_any = await session.execute(select(User).limit(1))
                if res_any.scalar_one_or_none() is None:
                    logger.info(f"Creating initial admin account: {settings.initial_admin_email}")
                    admin = User(
                        email=settings.initial_admin_email,
                        hashed_password=hash_password(settings.initial_admin_password),
                        role=UserRole.ADMIN,
                        is_active=True,
                        mfa_enabled=False,
                    )
                    session.add(admin)
                    await session.commit()
                    logger.info("Initial admin created successfully.")
            else:
                logger.debug("Database already has the initial admin.")
    except Exception as e:
        # Si l'erreur est liée à un objet déjà existant, on l'ignore (race condition résolue par PG)
        if "already exists" in str(e).lower():
            logger.debug(f"DB Object already exists, skipping: {e}")
        else:
            logger.error(f"Error during database initialization: {e}")
            raise
    finally:
        # Libérer le verrou (seulement si on l'avait pris)
        if retry_count < max_retries:
            await redis_client.delete(lock_key)
