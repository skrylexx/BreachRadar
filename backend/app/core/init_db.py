"""
BreachRadar WebUI — Initialisation de la base de données
=========================================================
Crée l'administrateur initial au premier démarrage si aucun utilisateur n'existe.
"""

import logging
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app import models # Ensure models are registered
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def initialize_database() -> None:
    """
    Initialise la DB au démarrage :
    - Synchronise le schéma.
    - Crée l'admin initial si aucun utilisateur n'existe.
    """
    # 1. Synchronisation du schéma
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
