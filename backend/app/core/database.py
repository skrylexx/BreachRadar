"""
BreachRadar WebUI — Database (SQLAlchemy Async)
=======================================================
Configuration of the PostgreSQL async engine and session factory.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ─── Async Engine ─────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # Log SQL only in dev
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Check the connection before each request
)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─── Declarative base ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""

    pass


# ─── FastAPI Dependency ───────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection: DB session per request, always cleanly closed."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
