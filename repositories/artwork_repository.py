"""
Artwork repository implementation using aiosql and raw database connections.
"""

import uuid
from datetime import datetime
from typing import Optional
import aiosql
from models.artwork_record import ArtworkRecord, SubjectExpansionRecord
from repositories.base import ArtworkRepository
from aiosql.adapters.generic import GenericAdapter


class ArtworkRepositoryImpl(ArtworkRepository):
    """
    Artwork repository implementation using aiosql for SQL queries
    and raw database connections for better compatibility.
    """

    def __init__(self, driver_adapter, connection):
        """
        Initialize repository with a connection manager.

        Args:
            driver_adapter: Database driver adapter (aiosqlite, asyncpg, etc.)
            connection_manager: Connection manager for acquiring database connections
        """
        self.driver_adapter = driver_adapter
        self.connection = connection
        self.queries = aiosql.from_path(
            "repositories/queries/artwork_queries.sql", driver_adapter=driver_adapter
        )

    async def get_cached_subject_expansion(
        self, artwork_id: str, subject: str, parent_expansion_id: Optional[str] = None
    ) -> Optional[SubjectExpansionRecord]:
        """
        Retrieve a cached subject expansion by artwork_id, subject, and parent_expansion_id.
        PostgreSQL generates the hash internally for efficient lookup.

        Args:
            artwork_id: Reference to the original artwork
            subject: The subject string to look up
            parent_expansion_id: Optional parent expansion ID for context

        Returns:
            SubjectExpansionRecord if found in cache, None otherwise
        """
        # Execute the query - PostgreSQL handles the hashing including parent_expansion_id
        results = await self.queries.get_cached_subject_expansion(
            self.connection, artwork_id=artwork_id, subject=subject, parent_expansion_id=parent_expansion_id
        )

        if not results or len(results) == 0:
            return None

        # Get the first (and should be only) result
        result = results[0]

        # Convert to domain model
        return SubjectExpansionRecord(
            expansion_id=result["expansion_id"],
            artwork_id=result["artwork_id"],
            subject=result["subject"],
            subject_hash=result["subject_hash"],
            expansion_xml=result["expansion_xml"],
            parent_expansion_id=result["parent_expansion_id"],
            created_at=result["created_at"],
        )

    async def save_artwork_explanation(
        self,
        artwork_id: str,
        explanation_xml: str,
        image_path: Optional[str] = None,
        creator_user_id: Optional[str] = None,
    ) -> ArtworkRecord:
        """
        Save an artwork explanation to the database.

        Args:
            artwork_id: Unique identifier for the artwork
            explanation_xml: The XML interpretation of the artwork
            image_path: Path to the image in storage (optional)
            creator_user_id: User who created/uploaded the artwork (optional for anonymous)

        Returns:
            ArtworkRecord with the saved data including timestamp
        """
        now = datetime.utcnow()

        if creator_user_id:
            await self.queries.ensure_user_profile(
                self.connection,
                user_id=creator_user_id,
            )

        # Execute the save query
        await self.queries.save_artwork_explanation(
            self.connection,
            artwork_id=artwork_id,
            explanation_xml=explanation_xml,
            image_path=image_path,
            creator_user_id=creator_user_id,
            created_at=now,
        )

        # Return the domain model
        return ArtworkRecord(
            artwork_id=artwork_id,
            explanation_xml=explanation_xml,
            image_path=image_path,
            creator_user_id=creator_user_id,
            created_at=now,
        )

    async def get_artwork_explanation(self, artwork_id: str) -> Optional[ArtworkRecord]:
        """
        Retrieve an artwork explanation from the database.

        Args:
            artwork_id: Unique identifier for the artwork

        Returns:
            ArtworkRecord if found, None otherwise
        """
        # Execute the query
        results = await self.queries.get_artwork_explanation(
            self.connection,
            artwork_id=artwork_id
        )

        if not results or len(results) == 0:
            return None

        # Get the first (and should be only) result
        result = results[0]

        # Convert to domain model
        return ArtworkRecord(
            artwork_id=result["artwork_id"],
            explanation_xml=result["explanation_xml"],
            image_path=result["image_path"],
            creator_user_id=result["creator_user_id"],
            created_at=result["created_at"],
        )

    async def save_subject_expansion(
        self,
        artwork_id: str,
        subject: str,
        expansion_xml: str,
        parent_expansion_id: Optional[str] = None,
    ) -> SubjectExpansionRecord:
        """
        Save a subject expansion to the database.

        Args:
            artwork_id: Reference to the original artwork
            subject: The subject that was expanded on
            expansion_xml: The XML expansion of the subject
            parent_expansion_id: Reference to parent expansion (None for root expansions)

        Returns:
            SubjectExpansionRecord with the saved data including timestamp
        """
        now = datetime.utcnow()
        expansion_id = str(uuid.uuid4())

        # Execute the save query - PostgreSQL generates the subject_hash
        await self.queries.save_subject_expansion(
            self.connection,
            expansion_id=expansion_id,
            artwork_id=artwork_id,
            subject=subject,
            expansion_xml=expansion_xml,
            parent_expansion_id=parent_expansion_id,
            created_at=now,
        )

        # Retrieve the saved record to get the PostgreSQL-generated subject_hash
        saved_record = await self.get_subject_expansion(expansion_id)
        if saved_record is None:
            raise RuntimeError(f"Failed to retrieve saved expansion: {expansion_id}")

        return saved_record

    async def get_subject_expansion(
        self, expansion_id: str
    ) -> Optional[SubjectExpansionRecord]:
        """
        Retrieve a subject expansion by expansion_id.

        Args:
            expansion_id: Unique identifier for the expansion

        Returns:
            SubjectExpansionRecord if found, None otherwise
        """
        # Execute the query
        results = await self.queries.get_subject_expansion(
            self.connection, expansion_id=expansion_id
        )

        if not results or len(results) == 0:
            return None

        # Get the first (and should be only) result
        result = results[0]

        # Convert to domain model
        return SubjectExpansionRecord(
            expansion_id=result["expansion_id"],
            artwork_id=result["artwork_id"],
            subject=result["subject"],
            subject_hash=result["subject_hash"],
            expansion_xml=result["expansion_xml"],
            parent_expansion_id=result["parent_expansion_id"],
            created_at=result["created_at"],
        )

    async def get_subject_expansions(
        self, artwork_id: str
    ) -> list[SubjectExpansionRecord]:
        """
        Retrieve all subject expansions for a given artwork.

        Args:
            artwork_id: Reference to the original artwork

        Returns:
            List of SubjectExpansionRecord, empty list if none found
        """
        # Execute the query
        results = await self.queries.get_subject_expansions(
            self.connection, artwork_id=artwork_id
        )

        # Convert to domain models
        return [
            SubjectExpansionRecord(
                expansion_id=row["expansion_id"],
                artwork_id=row["artwork_id"],
                subject=row["subject"],
                subject_hash=row["subject_hash"],
                expansion_xml=row["expansion_xml"],
                parent_expansion_id=row["parent_expansion_id"],
                created_at=row["created_at"],
            )
            for row in results
        ]

    async def save_user_artwork(self, user_id: str, artwork_id: str) -> None:
        """
        Save an artwork to a user's collection.

        Args:
            user_id: The user's ID
            artwork_id: The artwork's ID
        """
        now = datetime.utcnow()

        # Execute the save query
        await self.queries.save_user_artwork(
            self.connection,
            user_id=user_id,
            artwork_id=artwork_id,
            saved_at=now,
        )

    async def get_user_saved_artworks(self, user_id: str) -> list[ArtworkRecord]:
        """
        Retrieve all artworks saved by a user (metadata only, no XML).

        Args:
            user_id: The user's ID

        Returns:
            List of ArtworkRecord with metadata, empty list if none found
        """
        # Execute the query
        results = await self.queries.get_user_saved_artworks(
            self.connection, user_id=user_id
        )

        # Convert to domain models (without XML for performance)
        return [
            ArtworkRecord(
                artwork_id=row["artwork_id"],
                explanation_xml="",  # Not included in user artworks list
                image_path=row["image_path"],
                creator_user_id=row["creator_user_id"],
                created_at=row["saved_at"],  # Use saved_at for user's perspective
            )
            for row in results
        ]

    async def get_all_expansions_with_hierarchy(
        self, artwork_id: str
    ) -> list[SubjectExpansionRecord]:
        """
        Retrieve all subject expansions for a given artwork using recursive CTE.

        Args:
            artwork_id: Reference to the original artwork

        Returns:
            List of SubjectExpansionRecord with all expansions in hierarchy order
        """
        # Execute the recursive query
        results = await self.queries.get_all_expansions_with_hierarchy(
            self.connection, artwork_id=artwork_id
        )

        # Convert to domain models
        return [
            SubjectExpansionRecord(
                expansion_id=row["expansion_id"],
                artwork_id=row["artwork_id"],
                subject=row["subject"],
                subject_hash=row["subject_hash"],
                expansion_xml=row["expansion_xml"],
                parent_expansion_id=row["parent_expansion_id"],
                created_at=row["created_at"],
            )
            for row in results
        ]
