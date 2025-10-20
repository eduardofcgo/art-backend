# PostgreSQL Setup with asyncpg and Connection Pooling

This document explains how to configure and use PostgreSQL with asyncpg and connection pooling in the art-backend application.

## Environment Variables

Set the following environment variables to use PostgreSQL:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/art_backend
DATABASE_DRIVER_ADAPTER=asyncpg

# PostgreSQL Connection Pool Configuration (optional)
POSTGRES_MIN_CONNECTIONS=1
POSTGRES_MAX_CONNECTIONS=10
POSTGRES_COMMAND_TIMEOUT=60
```

## Database URL Format

The `DATABASE_URL` should follow this format:
```
postgresql+asyncpg://[user[:password]@][host][:port][/database][?param1=value1&...]
```

Examples:
- Local PostgreSQL: `postgresql+asyncpg://postgres:password@localhost:5432/art_backend`
- Cloud PostgreSQL: `postgresql+asyncpg://user:pass@db.example.com:5432/art_backend`
- With SSL: `postgresql+asyncpg://user:pass@host:5432/db?sslmode=require`

## Connection Pool Configuration

The connection pool is automatically created with these settings:

- **min_size**: Minimum number of connections in the pool (default: 1)
- **max_size**: Maximum number of connections in the pool (default: 10)
- **command_timeout**: Timeout for database commands in seconds (default: 60)

## Usage Example

```python
from dependencies.repository_provider import initialize_database, get_artwork_repository, shutdown_database
from config.settings import Settings

# Initialize settings
settings = Settings()

# Initialize database (creates connection pool for PostgreSQL)
await initialize_database(settings)

# Get repository instance (uses connection manager)
repo = await get_artwork_repository(settings)

# Use the repository - connections are managed automatically
artwork = await repo.save_artwork_explanation(
    artwork_id="test-123",
    explanation_xml="<artwork>...</artwork>",
    creator_user_id="user-456"
)

# Cleanup on application shutdown
await shutdown_database()
```

## Key Features

### Connection Pooling
- **Automatic**: Connection pool is created during `initialize_database()`
- **Efficient**: Reuses connections instead of creating new ones for each request
- **Configurable**: Pool size and timeouts can be adjusted via environment variables
- **Safe**: Connections are automatically returned to the pool after use

### Database Compatibility
- **SQLite**: Still supported with `DATABASE_DRIVER_ADAPTER=aiosqlite`
- **PostgreSQL**: New support with `DATABASE_DRIVER_ADAPTER=asyncpg`
- **Same Schema**: Uses the same schema.sql for both databases
- **Same API**: Repository interface remains unchanged

### Transaction Handling
- **SQLite**: Requires explicit `commit()` calls
- **PostgreSQL**: Auto-commits individual statements (asyncpg behavior)
- **Automatic**: The repository handles differences transparently

## Migration from SQLite to PostgreSQL

1. **Install asyncpg**: `pip install asyncpg>=0.29.0`
2. **Set environment variables**:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
   DATABASE_DRIVER_ADAPTER=asyncpg
   ```
3. **Create PostgreSQL database**:
   ```sql
   CREATE DATABASE art_backend;
   ```
4. **Run application**: The schema will be automatically created

## Performance Benefits

- **Connection Reuse**: Avoids connection overhead for each request
- **Concurrent Access**: Multiple requests can use different connections simultaneously
- **Resource Management**: Automatic connection cleanup and pool management
- **Scalability**: Configurable pool size based on application needs

## Error Handling

The system handles common PostgreSQL scenarios:

- **Connection failures**: Pool automatically retries with new connections
- **Timeout errors**: Configurable command timeout prevents hanging requests
- **Pool exhaustion**: Graceful handling when all connections are in use
- **Database unavailability**: Clear error messages for debugging

## Monitoring

Monitor your PostgreSQL connection pool:

```python
# Check pool status (if you have access to the pool object)
if hasattr(pool, 'get_size'):
    current_size = pool.get_size()
    idle_size = pool.get_idle_size()
    print(f"Pool: {current_size} total, {idle_size} idle")
```
