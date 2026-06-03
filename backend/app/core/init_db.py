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
from app.models.settings import SystemSettings
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

            # --- Migration manuelle pour les colonnes manquantes (Upgrade) ---
            # SQLAlchemy create_all ne rajoute pas de colonnes sur des tables existantes.
            # On force l'ajout des colonnes critiques si elles manquent.
            from sqlalchemy import text
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER DEFAULT 1 NOT NULL"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT FALSE NOT NULL"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_required BOOLEAN DEFAULT FALSE NOT NULL"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_secret VARCHAR(255)"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS mfa_backup_codes JSON"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_length INTEGER DEFAULT 0 NOT NULL"))

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
                        mfa_required=False,
                        mfa_secret=None,
                        mfa_backup_codes=None,
                    )
                    session.add(admin)
                    await session.commit()
                    logger.info("Initial admin created successfully.")
            else:
                logger.debug("Database already has the initial admin.")

            # 3. Synchroniser la configuration de Mock
            res_mock = await session.execute(select(SystemSettings).where(SystemSettings.key == "mock_data_enabled"))
            mock_setting = res_mock.scalar_one_or_none()
            if mock_setting is None:
                new_mock_setting = SystemSettings(key="mock_data_enabled", value=str(settings.mock_mode).lower())
                session.add(new_mock_setting)
                await session.commit()
            elif mock_setting.value != str(settings.mock_mode).lower():
                mock_setting.value = str(settings.mock_mode).lower()
                await session.commit()

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
