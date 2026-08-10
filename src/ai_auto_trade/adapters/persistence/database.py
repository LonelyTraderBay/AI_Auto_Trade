"""Database engine and session factory — Task 0.3.

Provides the SQLAlchemy async engine and session factory.
Connection URL is supplied via environment; no credential is hardcoded.
"""

import os

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def get_database_url() -> str:
    """Return the database URL from environment.

    Returns:
        Database URL string from DATABASE_URL env var.

    Raises:
        RuntimeError: If DATABASE_URL is not set.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is required. See .env.example for reference."
        )
    return url


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Args:
        database_url: PostgreSQL connection URL (asyncpg driver).

    Returns:
        Configured AsyncEngine instance.
    """
    return create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine.

    Args:
        engine: Async SQLAlchemy engine.

    Returns:
        Configured async sessionmaker.
    """
    return async_sessionmaker(engine, expire_on_commit=False)
