"""
BreachRadar WebUI — Base de données (SQLAlchemy Async)
=======================================================
Configuration de l'engine async PostgreSQL et session factory.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ─── Engine async ─────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL uniquement en dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Vérifie la connexion avant chaque requête
)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── Base déclarative ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base pour tous les modèles SQLAlchemy."""
    pass


# ─── Dependency FastAPI ───────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection : session DB par requête, toujours fermée proprement."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
