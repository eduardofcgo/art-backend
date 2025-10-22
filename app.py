"""
Art Backend API - Main application entry point.
"""

import logging
from litestar import Litestar, Router, get, Response
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.status_codes import HTTP_200_OK
from litestar.di import Provide
from serializer.asyncpg import serialize_asyncpg_record
import asyncpg

from controllers.artwork_explain import (
    explain_artwork,
    explain_artwork_from_image,
)
from controllers.artwork_retrieve import (
    get_artwork,
    get_artwork_image,
)
from controllers.artwork_expand import (
    expand_subject,
    get_expansion,
    get_artwork_expansions,
)
from controllers.user_artworks import (
    get_user_artworks,
)
from controllers.popular_artworks import get_popular_artworks
from middleware.auth import create_auth
from dependencies import get_ai_service, get_settings, authenticated_user_provider
from dependencies.repository_provider import (
    get_artwork_repository,
    initialize_database,
    shutdown_database,
)
from dependencies.storage_provider import artwork_storage_provider
from dependencies.url_resolver_provider import url_resolver_provider
from config.settings import Settings

# Configure logging with Litestar's LoggingConfig
logging_config = LoggingConfig(
    root={"level": logging.getLevelName(logging.INFO), "handlers": ["console"]},
    formatters={
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    loggers={
        "app": {"level": "INFO", "handlers": ["console"], "propagate": False},
        "litestar": {"level": "INFO", "handlers": ["console"], "propagate": False},
    },
)

logger = logging.getLogger(__name__)

# Create authentication middleware
auth = create_auth(
    token_secret=Settings().SUPABASE_JWT_SECRET,
    default_token_expiration=3600,  # 1 hour
)


# Create API router with shared dependencies for all /api/* routes
# All API routes automatically get repository, settings, storage_service, and authenticated_user injected
api_router = Router(
    path="/api",
    route_handlers=[get_artwork, get_artwork_image, get_expansion, get_user_artworks, get_artwork_expansions, get_popular_artworks],
    middleware=[auth.middleware],
    dependencies={
        "settings": Provide(get_settings, sync_to_thread=False),
        "repository": Provide(get_artwork_repository, sync_to_thread=False),
        "storage_service": artwork_storage_provider,
        "authenticated_user": authenticated_user_provider,
        "url_resolver": url_resolver_provider,
    },
)

# Create AI router with shared dependencies
# All routes in this router automatically get ai_service injected (settings and authenticated_user inherited from parent)
ai_router = Router(
    path="/ai",
    route_handlers=[explain_artwork, explain_artwork_from_image, expand_subject],
    dependencies={
        "ai_service": Provide(get_ai_service, sync_to_thread=False),
    },
)


# Health check endpoint
@get("/health", status_code=HTTP_200_OK)
async def health_check() -> str:
    """Health check endpoint"""
    return Response(content="healthy", media_type="text/plain", status_code=HTTP_200_OK)


# Configure CORS
cors_config = CORSConfig(
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Application lifecycle event handlers
async def startup() -> None:
    """Initialize database on application startup."""
    logger.info("Initializing database...")
    settings = Settings()
    await initialize_database(settings)
    logger.info("Database initialized successfully")


async def shutdown() -> None:
    """Cleanup database connections on application shutdown."""
    logger.info("Shutting down database connections...")
    await shutdown_database()
    logger.info("Database connections closed")


# Register ai_router as a child of api_router
api_router.register(ai_router)

# Create Litestar app with routers and exception handlers
app = Litestar(
    route_handlers=[api_router, health_check],
    cors_config=cors_config,
    logging_config=logging_config,
    on_app_init=[auth.on_app_init],
    on_startup=[startup],
    on_shutdown=[shutdown],
    type_encoders={asyncpg.Record: serialize_asyncpg_record},
    debug=True,  # Enable debug mode for detailed error logging
)
