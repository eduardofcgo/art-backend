"""
Controller for art interpretation business logic.
"""

import logging
import uuid
from typing import Optional
from litestar import Response
from litestar.datastructures import UploadFile
from litestar.status_codes import HTTP_200_OK
from litestar.dto import DTOData
from dataclasses import dataclass
from utils.image_processor import validate_and_process_image
from services.base import AIService
from models import ArtworkExplanation

logger = logging.getLogger(__name__)


async def explain_artwork_handler(
    data: UploadFile,
    *,
    ai_service: AIService,
) -> Response:
    """
    Handle artwork explanation request.

    Args:
        data: Uploaded image file
        ai_service: AI service instance injected by dependency injection

    Returns:
        Response with XML interpretation

    Raises:
        ValueError: If image validation fails
        Exception: If any other error occurs during processing
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

    # Temporary, we should integrate with database
    cache_name = f"artwork_{uuid.uuid4().hex[:16]}"

    # Get explanation from AI
    explanation_xml = await ai_service.explain_artwork(
        processed_image_data,
        cache_name=cache_name,
    )

    # Return XML response
    logger.info(
        f"Successfully generated artwork explanation response"
    )
    return Response(
        content=explanation_xml,
        media_type="application/xml",
        status_code=HTTP_200_OK,
    )


async def explain_artwork_with_cache_handler(
    data: UploadFile,
    *,
    ai_service: AIService,
) -> Response:
    """
    Handle artwork explanation request with caching enabled.

    Args:
        data: Uploaded image file
        ai_service: AI service instance injected by dependency injection

    Returns:
        Response with XML interpretation and cache identifier in headers

    Raises:
        ValueError: If image validation fails
        Exception: If any other error occurs during processing
    """
    logger.info(
        f"Received artwork explanation request with caching: filename={data.filename}, "
        f"content_type={data.content_type}"
    )

    # Generate unique cache name
    cache_name = f"artwork_{uuid.uuid4().hex[:16]}"

    # Read image data
    image_data = await data.read()
    logger.info(f"Read uploaded file: {len(image_data)} bytes")

    # Validate and process image
    processed_image_data = await validate_and_process_image(image_data)

    # Get explanation from AI with caching
    artwork_explanation = await ai_service.interpret_artwork_with_cache(
        processed_image_data, cache_name
    )

    # Return XML response with cache ID in header
    logger.info(
        f"Successfully generated artwork explanation response with cache: {artwork_explanation.cache_id}"
    )
    return Response(
        content=artwork_explanation.explanation_xml,
        media_type="application/xml",
        status_code=HTTP_200_OK,
        headers={"X-Cache-ID": artwork_explanation.cache_id},
    )


@dataclass
class ExpandSubjectRequest:
    """Request data for expanding on a wikilink subject."""
    subject: str


async def expand_subject_handler(
    data: ExpandSubjectRequest,
    artwork_id: str,
    *,
    ai_service: AIService,
) -> Response:
    """
    Handle wikilink subject expansion request.

    Args:
        data: Request data with subject
        artwork_id: Artwork identifier from the path
        ai_service: AI service instance injected by dependency injection

    Returns:
        Response with XML explanation

    Raises:
        ValueError: If request data is invalid
        Exception: If any other error occurs during processing
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

    # Get expansion from AI for the artwork_id and provided subject
    explanation_xml = await ai_service.expand_subject(
        artwork_id=artwork_id,
        subject=data.subject,
    )

    # Return XML response
    logger.info(f"Successfully generated subject expansion for: {data.subject}")
    return Response(
        content=explanation_xml,
        media_type="application/xml",
        status_code=HTTP_200_OK,
    )
