"""
Controller for artwork explanation endpoints.
"""

import logging
import uuid
from typing import Optional
from litestar import Response, post, Request
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Dependency
from dataclasses import dataclass
from dependencies.auth import AuthenticatedUser
from utils.image_processor import (
    processed_image_content_type,
    validate_and_process_image,
)
from services.base import AIService
from services.storage.artwork_image_storage import ArtworkImageStorage
from repositories.base import ArtworkRepository

logger = logging.getLogger(__name__)


@dataclass
class ExplainArtworkRequest:
    """Request data for explaining artwork by name."""
    
    artwork_name: str


@post("/artwork/explain", name="explain_artwork")
async def explain_artwork(
    request: Request,
    data: ExplainArtworkRequest,
    ai_service: AIService = Dependency(),
    repository: ArtworkRepository = Dependency(),
    authenticated_user: Optional[AuthenticatedUser] = Dependency(),
) -> Response:
    """
    Endpoint to explain artwork by name using AI.

    The AI provider is configured via the AI_PROVIDER environment variable.
    Supported providers: gemini

    Accepts: JSON with artwork_name field
    Returns: XML with the artwork explanation
    """
    logger.info(
        f"Received artwork explanation request by name: artwork_name={data.artwork_name}"
    )

    # Generate unique artwork ID
    artwork_id = str(uuid.uuid4())

    # Get authenticated user ID from injected dependency
    creator_user_id = authenticated_user.id if authenticated_user else None
    logger.info(f"🔐 Controller: Authenticated user ID: {creator_user_id}")

    # Get explanation from AI using artwork name
    explanation_xml = await ai_service.explain_artwork_by_name(
        artwork_name=data.artwork_name,
        cache_name=artwork_id,
    )

    # Save to database with creator user ID (no image path for name-based explanations)
    await repository.save_artwork_explanation(
        artwork_id=artwork_id,
        explanation_xml=explanation_xml,
        image_path=None,  # No image for name-based explanations
        artwork_name=data.artwork_name,  # Store artwork name for name-based explanations
        creator_user_id=creator_user_id,
    )
    logger.info(f"Saved artwork explanation to database: {artwork_id}")

    # If user is authenticated, automatically save to their collection
    # if creator_user_id:
    #     await repository.save_user_artwork(creator_user_id, artwork_id)
    #     logger.info(f"Auto-saved artwork to user's collection: {creator_user_id}")

    # Return redirect to the artwork endpoint
    logger.info(f"Successfully generated artwork explanation response")
    return Response(
        content="", status_code=303, headers={"Location": request.url_for("get_artwork", artwork_id=artwork_id)}
    )


@post("/artwork/explain-from-image", name="explain_artwork_from_image")
async def explain_artwork_from_image(
    request: Request,
    data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
    ai_service: AIService = Dependency(),
    repository: ArtworkRepository = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
    authenticated_user: Optional[AuthenticatedUser] = Dependency(),
) -> Response:
    """
    Endpoint to explain artwork from an uploaded image using AI vision models.

    The AI provider is configured via the AI_PROVIDER environment variable.
    Supported providers: gemini

    Accepts: multipart/form-data with an image file
    Returns: XML with the artwork explanation
    """
    logger.info(
        f"Received artwork explanation request: filename={data.filename}, "
        f"content_type={data.content_type}"
    )

    # Read image data
    image_data = await data.read()
    logger.info(f"Read uploaded file: {len(image_data)} bytes")

    # Validate and process image
    processed_image_data = await validate_and_process_image(image_data)

    # Generate unique artwork ID
    artwork_id = str(uuid.uuid4())

    # Get authenticated user ID from injected dependency
    creator_user_id = authenticated_user.id if authenticated_user else None
    logger.info(f"🔐 Controller: Authenticated user ID: {creator_user_id}")

    # Upload image to storage
    image_path = await storage_service.upload_artwork_image(
        artwork_id=artwork_id,
        image_data=processed_image_data,
        content_type=processed_image_content_type,
    )
    logger.info(f"Uploaded image to storage: {image_path}")

    # Get explanation from AI
    explanation_xml = await ai_service.explain_artwork(
        processed_image_data,
        cache_name=artwork_id,
    )

    # Save to database with image path and creator user ID
    await repository.save_artwork_explanation(
        artwork_id=artwork_id,
        explanation_xml=explanation_xml,
        image_path=image_path,
        creator_user_id=creator_user_id,
    )
    logger.info(f"Saved artwork explanation to database: {artwork_id}")

    # If user is authenticated, automatically save to their collection
    if creator_user_id:
        await repository.save_user_artwork(creator_user_id, artwork_id)
        logger.info(f"Auto-saved artwork to user's collection: {creator_user_id}")

    # Return redirect to the artwork endpoint
    logger.info(f"Successfully generated artwork explanation response")
    return Response(
        content="", status_code=303, headers={"Location": request.url_for("get_artwork", artwork_id=artwork_id)}
    )
