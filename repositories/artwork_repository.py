"""
Artwork repository implementation using aiosql and raw database connections.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import aiosql
from repositories.base import ArtworkRepository


class ArtworkRepositoryImpl(ArtworkRepository):

    def __init__(self, driver_adapter, connection):
        self.driver_adapter = driver_adapter
        self.connection = connection
        self.queries = aiosql.from_path(
            "repositories/queries/artwork_queries.sql", driver_adapter=driver_adapter
        )

    async def get_cached_subject_expansion(
        self, artwork_id: str, subject: str, parent_expansion_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        results = await self.queries.get_cached_subject_expansion(
            self.connection, artwork_id=artwork_id, subject=subject, parent_expansion_id=parent_expansion_id
        )

        if not results or len(results) == 0:
            return None

        return results[0]

    async def save_artwork_explanation(
        self,
        artwork_id: str,
        explanation_xml: str,
        image_path: Optional[str] = None,
        artwork_name: Optional[str] = None,
        creator_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()

        if creator_user_id:
            await self.queries.ensure_user_profile(
                self.connection,
                user_id=creator_user_id,
            )

        return await self.queries.save_artwork_explanation(
            self.connection,
            artwork_id=artwork_id,
            explanation_xml=explanation_xml,
            image_path=image_path,
            artwork_name=artwork_name,
            creator_user_id=creator_user_id,
            created_at=now,
        )

    async def get_artwork_explanation(self, artwork_id: str) -> Optional[Dict[str, Any]]:
        results = await self.queries.get_artwork_explanation(
            self.connection,
            artwork_id=artwork_id
        )

        if not results or len(results) == 0:
            return None

        return results[0]

    async def save_subject_expansion(
        self,
        artwork_id: str,
        subject: str,
        expansion_xml: str,
        parent_expansion_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.utcnow()
        expansion_id = str(uuid.uuid4())

        await self.queries.save_subject_expansion(
            self.connection,
            expansion_id=expansion_id,
            artwork_id=artwork_id,
            subject=subject,
            expansion_xml=expansion_xml,
            parent_expansion_id=parent_expansion_id,
            created_at=now,
        )

        saved_record = await self.get_subject_expansion(expansion_id)
        if saved_record is None:
            raise ValueError(f"Failed to retrieve saved expansion: {expansion_id}")

        return saved_record

    async def get_subject_expansion(
        self, expansion_id: str
    ) -> Optional[Dict[str, Any]]:
        results = await self.queries.get_subject_expansion(
            self.connection, expansion_id=expansion_id
        )

        if not results or len(results) == 0:
            return None

        return results[0]

    async def get_subject_expansions(
        self, artwork_id: str
    ) -> list[Dict[str, Any]]:
        results = await self.queries.get_subject_expansions(
            self.connection, artwork_id=artwork_id
        )

        return results

    async def save_user_artwork(self, user_id: str, artwork_id: str) -> None:
        now = datetime.utcnow()

        await self.queries.save_user_artwork(
            self.connection,
            user_id=user_id,
            artwork_id=artwork_id,
            saved_at=now,
        )

    async def get_user_saved_artworks(self, user_id: str) -> list[Dict[str, Any]]:
        results = await self.queries.get_user_saved_artworks(
            self.connection, user_id=user_id
        )

        return results

    async def get_all_expansions_with_hierarchy(
        self, artwork_id: str
    ) -> list[Dict[str, Any]]:
        results = await self.queries.get_all_expansions_with_hierarchy(
            self.connection, artwork_id=artwork_id
        )

        return results
