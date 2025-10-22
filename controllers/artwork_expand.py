"""
Controller for artwork subject expansion endpoints.
"""

import logging
from typing import Optional
from litestar import Response, post, get
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from litestar.params import Dependency
from dataclasses import dataclass
from services.base import AIService
from repositories.base import ArtworkRepository
from litestar import Request

logger = logging.getLogger(__name__)


@dataclass
class ExpandSubjectRequest:
    """Request data for expanding on a wikilink subject."""

    artwork_id: str
    subject: str
    parent_expansion_id: Optional[str] = None


@post("/artwork/expand", name="expand_subject")
async def expand_subject(
    request: Request,
    data: ExpandSubjectRequest,
    ai_service: AIService = Dependency(),
    repository: ArtworkRepository = Dependency(),
) -> Response:
    """
    Endpoint to expand on a wikilink subject in the context of the original artwork.

    This endpoint reuses the cached image context from the original artwork interpretation.

    Example request body:
    {
        "artwork_id": "123e4567-e89b-12d3-a456-426614174000",
        "subject": "Impressionism",
        "parent_expansion_id": "123e4567-e89b-12d3-a456-426614174000"
    }

    Returns: Redirect to the created expansion resource
    """
    logger.info(
        f"Received subject expansion request: subject={data.subject}, "
        f"artwork_id={data.artwork_id}"
    )

    # Validate inputs
    if not data.subject or not data.subject.strip():
        raise ValueError("Subject cannot be empty")

    if not data.artwork_id or not data.artwork_id.strip():
        raise ValueError("Artwork ID cannot be empty")

    # Check if expansion already exists in cache
    cached_expansion = await repository.get_cached_subject_expansion(
        artwork_id=data.artwork_id,
        subject=data.subject,
        parent_expansion_id=data.parent_expansion_id,
    )
    
    if cached_expansion is not None:
        logger.info(f"Found cached expansion for subject: {data.subject}")
        expansion_record = cached_expansion
    else:
        # Retrieve original artwork explanation from database
        artwork_record = await repository.get_artwork_explanation(data.artwork_id)
        if artwork_record is None:
            raise ValueError(f"Artwork not found: {data.artwork_id}")

        # Get expansion from AI for the artwork_id and provided subject
        expansion_xml = await ai_service.expand_subject(
            artwork_id=data.artwork_id,
            original_artwork_explanation=artwork_record["explanation_xml"],
            subject=data.subject,
        )

        # Save subject expansion to database
        expansion_record = await repository.save_subject_expansion(
            artwork_id=data.artwork_id,
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
        headers={"Location": request.url_for("get_expansion", expansion_id=str(expansion_record["expansion_id"]))},
    )


@get("/expansion/{expansion_id:str}", name="get_expansion")
async def get_expansion(
    expansion_id: str,
    repository: ArtworkRepository = Dependency(),
) -> Response:
    """
    Endpoint to retrieve a subject expansion by ID.

    Path parameter:
        expansion_id: The unique identifier for the expansion

    Returns: JSON object with expansion data or 404 if not found
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

    logger.info(f"Successfully retrieved subject expansion: {expansion_id}")
    return Response(
        content=expansion_record,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )


@get("/artwork/{artwork_id:str}/expansions", name="get_artwork_expansions")
async def get_artwork_expansions(
    artwork_id: str,
    repository: ArtworkRepository = Dependency(),
) -> Response:
    """
    Endpoint to retrieve all expansions for an artwork in a hierarchical tree structure.

    Path parameter:
        artwork_id: The unique identifier for the artwork

    Returns: JSON array with hierarchical expansion tree or 404 if artwork not found
    """
    logger.info(f"Received artwork expansions request: artwork_id={artwork_id}")

    # Retrieve all expansions for the artwork using recursive query
    all_expansions = await repository.get_all_expansions_with_hierarchy(artwork_id)
    
    if not all_expansions:
        logger.warning(f"No expansions found for artwork: {artwork_id}")
        return Response(
            content=[],
            media_type="application/json",
            status_code=HTTP_200_OK,
        )

    # Build hierarchical tree structure
    def build_tree(expansions, parent_id=None):
        """Build tree structure from flat list of expansions."""
        children = []
        for expansion in expansions:
            if expansion["parent_expansion_id"] == parent_id:
                child = {
                    "id": expansion["expansion_id"],
                    "subject": expansion["subject"],
                    "created_at": expansion["created_at"].isoformat(),
                    "sub_expansions": build_tree(expansions, expansion["expansion_id"])
                }
                children.append(child)
        
        return children

    # Build the tree starting from root expansions (parent_expansion_id = None)
    tree = build_tree(all_expansions, None)

    logger.info(f"Successfully built expansion tree with {len(tree)} root expansions for artwork: {artwork_id}")
    return Response(
        content=tree,
        media_type="application/json",
        status_code=HTTP_200_OK,
    )
