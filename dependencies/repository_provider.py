"""
Dependency injection for repository services with connection pooling support.
"""

import os
from typing import Optional, Protocol, runtime_checkable
from contextlib import asynccontextmanager
from config.settings import Settings
from repositories.artwork_repository import ArtworkRepositoryImpl
from repositories.base import ArtworkRepository


@runtime_checkable
class ConnectionManager(Protocol):
    """
    Protocol for managing database connections.
    Allows repositories to acquire and release connections as needed.
    """
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Context manager for acquiring and automatically releasing a database connection.
        
        Usage:
            async with connection_manager.get_connection() as conn:
                # Use connection
                pass
        """
        ...


# Global connection pool for PostgreSQL
_postgres_pool: Optional[object] = None


class SQLiteConnectionManager:
    """Connection manager for SQLite database."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
    
    @asynccontextmanager
    async def get_connection(self):
        import aiosqlite
        connection = await aiosqlite.connect(self.database_path)
        connection.row_factory = aiosqlite.Row
        
        # Configure SQLite for optimal performance and reliability
        # These settings are safe defaults that work well for most applications
        await connection.execute("PRAGMA journal_mode = WAL")  # WAL mode for better concurrency
        await connection.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and performance
        await connection.execute("PRAGMA cache_size = -64000")  # 64MB cache for better performance
        
        try:
            yield connection
            # Explicitly commit any pending transactions before closing
            await connection.commit()
        except Exception:
            # Rollback on any exception
            await connection.rollback()
            raise
        finally:
            await connection.close()


class PostgreSQLConnectionManager:
    """Connection manager for PostgreSQL database using connection pool."""
    
    def __init__(self, pool):
        self.pool = pool
    
    @asynccontextmanager
    async def get_connection(self):
        connection = await self.pool.acquire()
        try:
            yield connection
        finally:
            await self.pool.release(connection)


async def initialize_database(settings: Settings) -> None:
    """
    Initialize the database connection and create tables from schema.sql.
    Should be called on application startup.

    Args:
        settings: Application settings containing DATABASE_URL
    """
    if settings.DATABASE_DRIVER_ADAPTER == "aiosqlite":
        import aiosqlite

        # Read the schema.sql file
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "repositories", "schema.sql"
        )
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Connect to database and execute schema
        connection = await aiosqlite.connect(settings.DATABASE_FILE_PATH)
        try:
            # Execute the entire schema at once
            await connection.executescript(schema_sql)
            await connection.commit()
        finally:
            await connection.close()
            
    elif settings.DATABASE_DRIVER_ADAPTER == "asyncpg":
        import asyncpg
        from urllib.parse import urlparse
        
        global _postgres_pool
        
        # Parse the database URL
        parsed_url = urlparse(settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
        
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
            f"Database initialization not implemented for driver: {settings.DATABASE_DRIVER_ADAPTER}"
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
    if settings.DATABASE_DRIVER_ADAPTER == "aiosqlite":
        connection_manager = SQLiteConnectionManager(settings.DATABASE_FILE_PATH)
        return ArtworkRepositoryImpl(settings.DATABASE_DRIVER_ADAPTER, connection_manager)
        
    elif settings.DATABASE_DRIVER_ADAPTER == "asyncpg":
        global _postgres_pool
        
        if not _postgres_pool:
            raise RuntimeError(
                "PostgreSQL connection pool not initialized. Call initialize_database() first."
            )
        
        connection_manager = PostgreSQLConnectionManager(_postgres_pool)
        return ArtworkRepositoryImpl(settings.DATABASE_DRIVER_ADAPTER, connection_manager)
    else:
        raise ValueError(
            f"Unsupported database driver adapter: {settings.DATABASE_DRIVER_ADAPTER}"
        )


