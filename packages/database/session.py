"""TraceX database session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
import logging

from .models import Base

logger = logging.getLogger(__name__)

engine = None
async_session_maker = None


def init_database(database_url: str) -> None:
    """Initialize database engine and session maker."""
    global engine, async_session_maker

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        poolclass=NullPool if "sqlite" in database_url else None,
    )

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("Database initialized")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as context manager."""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all database tables."""
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")


async def drop_tables() -> None:
    """Drop all database tables."""
    if engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.warning("Database tables dropped")


async def close_database() -> None:
    """Close database connections."""
    if engine is not None:
        await engine.dispose()
        logger.info("Database connections closed")


async def run_migrations() -> None:
    """Run database migrations using Alembic."""
    import subprocess
    import sys

    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(f"Migration failed: {result.stderr}")
        else:
            logger.info("Migrations completed")
    except Exception as e:
        logger.warning(f"Migration command not available: {e}")


def get_engine():
    """Get the database engine."""
    return engine


def get_session_maker():
    """Get the session maker."""
    return async_session_maker
