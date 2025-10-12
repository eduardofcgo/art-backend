"""
Art Backend API - Main application entry point.
"""

import logging
from litestar import Litestar, Router, post, Response
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Dependency
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig
from litestar.status_codes import HTTP_200_OK
from litestar.di import Provide

from controllers.art_controller import (
    explain_artwork_handler,
    expand_subject_handler,
    ExpandSubjectRequest,
)
from middleware.error_handler import value_error_handler, generic_exception_handler
from dependencies import get_ai_service, get_settings
from config.settings import Settings
from services.base import AIService

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


@post("/artwork/explain")
async def explain_artwork(
    data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
    ai_service: AIService = Dependency(),
) -> Response:
    """
    Endpoint to explain artwork from an uploaded image using AI vision models.

    The AI provider is configured via the AI_PROVIDER environment variable.
    Supported providers: openai, gemini, anthropic

    Accepts: multipart/form-data with an image file
    Returns: XML with the artwork explanation
    """
    return await explain_artwork_handler(data, ai_service=ai_service)

@post("/artwork/{artwork_id:str}/subject")
async def expand_subject(
    data: ExpandSubjectRequest,
    artwork_id: str,
    ai_service: AIService = Dependency(),
) -> Response:
    """
    Endpoint to expand on a wikilink subject in the context of the original artwork.
    
    This endpoint reuses the cached image context from the original artwork interpretation.
    
    Path parameter:
        artwork_id: The cache identifier returned from the initial artwork explanation
    
    Request body:
    {
        "subject": "Impressionism"
    }
    
    Returns: XML with the in-depth subject expansion
    """
    return await expand_subject_handler(data, artwork_id, ai_service=ai_service)


# Create AI router with shared dependencies
# All routes in this router automatically get ai_service and settings injected
ai_router = Router(
    path="/api/ai",
    route_handlers=[explain_artwork, expand_subject],
    dependencies={
        "settings": Provide(get_settings, sync_to_thread=False),
        "ai_service": Provide(get_ai_service, sync_to_thread=False),
    },
)


# Health check endpoint
@post("/health", status_code=HTTP_200_OK)
async def health_check() -> str:
    """Health check endpoint"""
    return Response(content="healthy", media_type="text/plain", status_code=HTTP_200_OK)


# Configure CORS
cors_config = CORSConfig(
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Create Litestar app with routers and exception handlers
app = Litestar(
    route_handlers=[ai_router, health_check],
    cors_config=cors_config,
    logging_config=logging_config,
    exception_handlers={
        ValueError: value_error_handler,
        Exception: generic_exception_handler,
    },
    debug=True,  # Enable debug mode for detailed error logging
)
