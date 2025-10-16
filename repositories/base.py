"""
Base protocol for artwork repositories.
"""

from typing import Protocol, Optional, runtime_checkable
from models.artwork_record import ArtworkRecord, SubjectExpansionRecord


@runtime_checkable
class ArtworkRepository(Protocol):
    """
    Protocol defining the interface for artwork persistence operations.
    """

    async def save_artwork_explanation(
        self,
        artwork_id: str,
        explanation_xml: str,
        creator_user_id: Optional[str] = None,
    ) -> ArtworkRecord:
        """
        Save an artwork explanation to the repository.

        Args:
            artwork_id: Unique identifier for the artwork
            explanation_xml: The XML interpretation of the artwork
            creator_user_id: User who created/uploaded the artwork (optional for anonymous)

        Returns:
            ArtworkRecord with the saved data including timestamp

        Raises:
            Exception: If save operation fails
        """
        ...

    async def get_artwork_explanation(self, artwork_id: str) -> Optional[ArtworkRecord]:
        """
        Retrieve an artwork explanation from the repository.

        Args:
            artwork_id: Unique identifier for the artwork

        Returns:
            ArtworkRecord if found, None otherwise

        Raises:
            Exception: If retrieval operation fails
        """
        ...

    async def save_subject_expansion(
        self,
        artwork_id: str,
        subject: str,
        expansion_xml: str,
        parent_expansion_id: Optional[str] = None,
    ) -> SubjectExpansionRecord:
        """
        Save a subject expansion to the repository.

        Args:
            artwork_id: Reference to the original artwork
            subject: The subject that was expanded on
            expansion_xml: The XML expansion of the subject
            parent_expansion_id: Reference to parent expansion (None for root expansions)

        Returns:
            SubjectExpansionRecord with the saved data including timestamp

        Raises:
            Exception: If save operation fails
        """
        ...

    async def get_subject_expansion(
        self, expansion_id: str
    ) -> Optional[SubjectExpansionRecord]:
        """
        Retrieve a subject expansion by expansion_id.

        Args:
            expansion_id: Unique identifier for the expansion

        Returns:
            SubjectExpansionRecord if found, None otherwise

        Raises:
            Exception: If retrieval operation fails
        """
        ...

    async def get_subject_expansions(
        self, artwork_id: str
    ) -> list[SubjectExpansionRecord]:
        """
        Retrieve all subject expansions for a given artwork.

        Args:
            artwork_id: Reference to the original artwork

        Returns:
            List of SubjectExpansionRecord, empty list if none found

        Raises:
            Exception: If retrieval operation fails
        """
        ...

    async def save_user_artwork(self, user_id: str, artwork_id: str) -> None:
        """
        Save an artwork to a user's collection.

        Args:
            user_id: The user's ID
            artwork_id: The artwork's ID

        Raises:
            Exception: If save operation fails
        """
        ...

    async def get_user_saved_artworks(self, user_id: str) -> list[ArtworkRecord]:
        """
        Retrieve all artworks saved by a user (metadata only, no XML).

        Args:
            user_id: The user's ID

        Returns:
            List of ArtworkRecord with metadata, empty list if none found

        Raises:
            Exception: If retrieval operation fails
        """
        ...
