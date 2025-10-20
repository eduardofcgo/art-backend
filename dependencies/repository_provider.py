"""
Dependency injection for repository services with connection pooling support.
"""

import os
from typing import Optional, Protocol, runtime_checkable
from contextlib import asynccontextmanager
from config.settings import Settings
from repositories.artwork_repository import ArtworkRepositoryImpl
from repositories.base import ArtworkRepository


# Global connection pool for PostgreSQL
_postgres_pool: Optional[object] = None



async def initialize_database(settings: Settings) -> None:
    """
    Initialize the database connection and create tables from schema.sql.
    Should be called on application startup.

    Args:
        settings: Application settings containing DATABASE_URL
    """
    if settings.DATABASE_DRIVER_ADAPTER == "asyncpg":
        import asyncpg
        from urllib.parse import urlparse

        global _postgres_pool

        # Parse the database URL
        parsed_url = urlparse(
            settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        )

        # Create connection pool
        _postgres_pool = await asyncpg.create_pool(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path[1:],  # Remove leading slash
            min_size=settings.POSTGRES_MIN_CONNECTIONS,
            max_size=settings.POSTGRES_MAX_CONNECTIONS,
            command_timeout=settings.POSTGRES_COMMAND_TIMEOUT,
        )

        # Read and execute schema
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "repositories", "schema.sql"
        )
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Execute schema using the pool
        async with _postgres_pool.acquire() as connection:
            await connection.execute(schema_sql)
    else:
        raise ValueError(
            f"Database initialization not implemented: {settings.DATABASE_DRIVER_ADAPTER}"
        )


async def shutdown_database() -> None:
    """
    Cleanup database connections.
    Should be called on application shutdown.
    """
    global _postgres_pool
    if _postgres_pool:
        await _postgres_pool.close()
        _postgres_pool = None


async def get_artwork_repository(settings: Settings) -> ArtworkRepository:
    """
    Get an artwork repository instance with appropriate connection manager.

    Args:
        settings: Application settings containing database configuration

    Returns:
        ArtworkRepository instance configured for the specified database

    Raises:
        ValueError: If the database driver adapter is not supported
    """
    if settings.DATABASE_DRIVER_ADAPTER == "asyncpg":
        global _postgres_pool

        if not _postgres_pool:
            raise RuntimeError(
                "PostgreSQL connection pool not initialized. Call initialize_database() first."
            )

        return ArtworkRepositoryImpl(
            # aiosql implicitly handles the connection for us.
            settings.DATABASE_DRIVER_ADAPTER, _postgres_pool 
        )
    else:
        raise ValueError(
            f"Unsupported database driver adapter: {settings.DATABASE_DRIVER_ADAPTER}"
        )
