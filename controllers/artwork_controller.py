"""
Controller for art interpretation business logic.
"""

import logging
import uuid
from typing import Optional
from litestar import Response, post, get, Request
from litestar.datastructures import UploadFile
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from litestar.dto import DTOData
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
from models import ArtworkExplanation
from repositories.base import ArtworkRepository

logger = logging.getLogger(__name__)


@post("/artwork/explain")
async def explain_artwork(
    data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
    ai_service: AIService = Dependency(),
    repository: ArtworkRepository = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
    authenticated_user: Optional[AuthenticatedUser] = Dependency(),
) -> Response:
    """
    Endpoint to explain artwork from an uploaded image using AI vision models.

    The AI provider is configured via the AI_PROVIDER environment variable.
    Supported providers: openai, gemini, anthropic

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
        content="", status_code=303, headers={"Location": f"/api/artwork/{artwork_id}"}
    )


@dataclass
class ExpandSubjectRequest:
    """Request data for expanding on a wikilink subject."""

    artwork_id: str
    subject: str
    parent_expansion_id: Optional[str] = None


@post("/artwork/expand")
async def expand_subject(
    data: ExpandSubjectRequest,
    artwork_id: str,
    ai_service: AIService = Dependency(),
    repository: ArtworkRepository = Dependency(),
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
    logger.info(
        f"Received subject expansion request: subject={data.subject}, "
        f"artwork_id={artwork_id}"
    )

    # Validate inputs
    if not data.subject or not data.subject.strip():
        raise ValueError("Subject cannot be empty")

    if not artwork_id or not artwork_id.strip():
        raise ValueError("Artwork ID cannot be empty")

    # Retrieve original artwork explanation from database
    artwork_record = await repository.get_artwork_explanation(artwork_id)
    if artwork_record is None:
        raise ValueError(f"Artwork not found: {artwork_id}")

    # Get expansion from AI for the artwork_id and provided subject
    expansion_xml = await ai_service.expand_subject(
        artwork_id=artwork_id,
        original_artwork_explanation=artwork_record.explanation_xml,
        subject=data.subject,
    )

    # Save subject expansion to database
    expansion_record = await repository.save_subject_expansion(
        artwork_id=artwork_id,
        subject=data.subject,
        expansion_xml=expansion_xml,
        parent_expansion_id=data.parent_expansion_id,
    )
    logger.info(f"Saved subject expansion to database: {data.subject}")

    # Return redirect to the expansion endpoint
    logger.info(f"Successfully generated subject expansion for: {data.subject}")
    return Response(
        content="",
        status_code=303,
        headers={"Location": f"/api/expansion/{expansion_record.expansion_id}"},
    )


@get("/artwork/{artwork_id:str}")
async def get_artwork(
    artwork_id: str,
    repository: ArtworkRepository = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
) -> Response:
    """
    Endpoint to retrieve an artwork explanation by ID.

    Path parameter:
        artwork_id: The unique identifier for the artwork

    Returns: XML with the artwork explanation or 404 if not found
    """
    logger.info(f"Received artwork retrieval request: artwork_id={artwork_id}")

    # Retrieve artwork explanation from database
    artwork_record = await repository.get_artwork_explanation(artwork_id)
    if artwork_record is None:
        logger.warning(f"Artwork not found: {artwork_id}")
        return Response(
            content="Artwork not found",
            status_code=HTTP_404_NOT_FOUND,
        )

    # Generate image endpoint URL if available
    image_url = None
    if artwork_record.image_path:
        image_url = f"/api/artwork/{artwork_record.artwork_id}/image"

    # Return JSON response with both XML and image URL
    response_data = {
        "artwork_id": artwork_record.artwork_id,
        "explanation_xml": artwork_record.explanation_xml,
        "image_url": image_url,
        "created_at": artwork_record.created_at.isoformat(),
    }

    logger.info(f"Successfully retrieved artwork explanation: {artwork_id}")
    return Response(
        content=response_data,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )


@get("/artwork/{artwork_id:str}/image")
async def get_artwork_image(
    artwork_id: str,
    size: Optional[str] = None,
    repository: ArtworkRepository = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
) -> Response:
    """
    Endpoint to get the artwork image by redirecting to the signed URL.

    Path parameter:
        artwork_id: The unique identifier for the artwork

    Query parameter:
        size: Optional size parameter (currently supports "sm" for 200x200)

    Returns: Redirect to the signed URL of the image or 404 if not found
    """
    logger.info(f"Received artwork image request: artwork_id={artwork_id}, size={size}")

    # Retrieve artwork explanation from database
    artwork_record = await repository.get_artwork_explanation(artwork_id)
    if artwork_record is None:
        logger.warning(f"Artwork not found: {artwork_id}")
        return Response(
            content="Artwork not found",
            status_code=HTTP_404_NOT_FOUND,
        )

    # Check if image path exists
    if not artwork_record.image_path:
        logger.warning(f"No image path found for artwork: {artwork_id}")
        return Response(
            content="Image not found",
            status_code=HTTP_404_NOT_FOUND,
        )

    # Map size parameter to dimensions
    width = None
    height = None
    if size == "sm":
        width = 200
        height = 200

    # Generate signed URL for image with optional transformation
    image_url = await storage_service.get_image_url(
        artwork_record.image_path, width=width, height=height
    )
    logger.info(f"Generated signed URL for image: {artwork_record.image_path}")

    # Return redirect to the signed URL
    return Response(content="", status_code=302, headers={"Location": image_url})


@get("/expansion/{expansion_id:str}")
async def get_expansion(
    expansion_id: str,
    repository: ArtworkRepository = Dependency(),
) -> Response:
    """
    Endpoint to retrieve a subject expansion by ID.

    Path parameter:
        expansion_id: The unique identifier for the expansion

    Returns: XML with the subject expansion or 404 if not found
    """
    logger.info(f"Received expansion retrieval request: expansion_id={expansion_id}")

    # Retrieve subject expansion from database
    expansion_record = await repository.get_subject_expansion(expansion_id)
    if expansion_record is None:
        logger.warning(f"Expansion not found: {expansion_id}")
        return Response(
            content="Expansion not found",
            status_code=HTTP_404_NOT_FOUND,
        )

    # Return XML response
    logger.info(f"Successfully retrieved subject expansion: {expansion_id}")
    return Response(
        content=expansion_record.expansion_xml,
        media_type="application/xml",
        status_code=HTTP_200_OK,
    )


@get("/user/{user_id:str}/artworks")
async def get_user_artworks(
    user_id: str,
    repository: ArtworkRepository = Dependency(),
    authenticated_user: Optional[AuthenticatedUser] = Dependency(),
) -> Response:
    """
    Endpoint to retrieve all artworks saved by a user.

    Path parameter:
        user_id: The unique identifier for the user

    Returns: JSON array with artwork metadata (no XML) or 404 if user not found
    """
    logger.info(f"Received user artworks request: user_id={user_id}")

    # Retrieve user's saved artworks from database
    saved_artworks = await repository.get_user_saved_artworks(user_id)

    # Build response with image endpoint URLs
    artworks_data = []
    for artwork in saved_artworks:
        # Generate image endpoint URL if image is available
        image_url = None
        if artwork.image_path:
            image_url = f"/api/artwork/{artwork.artwork_id}/image?size=sm"

        artworks_data.append(
            {
                "artwork_id": artwork.artwork_id,
                "image_url": image_url,
                "created_at": artwork.created_at.isoformat(),
                "creator_user_id": artwork.creator_user_id,
            }
        )

    # Get authenticated user ID from injected dependency
    authenticated_user_id = authenticated_user.id if authenticated_user else None
    logger.info(
        f"🔍 Controller: Authenticated user ID from JWT: {authenticated_user_id}"
    )

    # Optional: You can verify the authenticated user matches the requested user_id
    if authenticated_user_id and authenticated_user_id != user_id:
        logger.warning(
            f"⚠️ User {authenticated_user_id} is accessing artworks of user {user_id}"
        )

    logger.info(
        f"Successfully retrieved {len(artworks_data)} artworks for user: {user_id}"
    )
    return Response(
        content=artworks_data,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )
