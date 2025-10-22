"""
Controller for user artwork endpoints.
"""

import logging
from typing import Optional
from litestar import Response, get, Request
from litestar.status_codes import HTTP_200_OK
from litestar.params import Dependency
from dependencies.auth import AuthenticatedUser
from repositories.base import ArtworkRepository
from services.storage.artwork_image_storage import ArtworkImageStorage

logger = logging.getLogger(__name__)


@get("/user/{user_id:str}/artworks", name="get_user_artworks")
async def get_user_artworks(
    request: Request,
    user_id: str,
    repository: ArtworkRepository = Dependency(),
    authenticated_user: Optional[AuthenticatedUser] = Dependency(),
    storage_service: ArtworkImageStorage = Dependency(),
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

    for artwork in saved_artworks:
        if image_path := artwork.get("image_path"):
            artwork["image_url"] = await storage_service.get_image_url(image_path)
            del artwork["image_path"]

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
        f"Successfully retrieved {len(saved_artworks)} artworks for user: {user_id}"
    )
    return Response(
        content=saved_artworks,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )
