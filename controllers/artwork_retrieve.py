"""
Controller for artwork retrieval endpoints.
"""

import logging
from typing import Optional
from litestar import Response, get, Request
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from litestar.params import Dependency
from repositories.base import ArtworkRepository
from services.storage.artwork_image_storage import ArtworkImageStorage

logger = logging.getLogger(__name__)


@get("/artwork/{artwork_id:str}", name="get_artwork")
async def get_artwork(
    request: Request,
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
    if image_path := artwork_record.get("image_path"):
        artwork_record["image_url"] = await storage_service.get_image_url(image_path)
        del artwork_record["image_path"]

    logger.info(f"Successfully retrieved artwork explanation: {artwork_id}")
    return Response(
        content=artwork_record,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )


@get("/artwork/{artwork_id:str}/image", name="get_artwork_image")
async def get_artwork_image(
    artwork_id: str,
    size: Optional[str] = None,
    repository: ArtworkRepository = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
) -> Response:
    """
    Endpoint to get the artwork image by redirecting to the public URL.

    Path parameter:
        artwork_id: The unique identifier for the artwork

    Query parameter:
        size: Optional size parameter (currently supports "sm" for 200x200)

    Returns: Redirect to the public URL of the image or 404 if not found
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
    if not artwork_record["image_path"]:
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

    # Generate public URL for image with optional transformation
    image_url = await storage_service.get_image_url(
        artwork_record["image_path"], width=width, height=height
    )
    logger.info(f"Generated public URL for image: {artwork_record['image_path']}")

    # Return redirect to the public URL
    return Response(content="", status_code=302, headers={"Location": image_url})
