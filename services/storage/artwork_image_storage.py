"""
Artwork-specific image storage service.
"""

import logging
from typing import Optional
from services.storage.base import StorageService

logger = logging.getLogger(__name__)


class ArtworkImageStorage:
    """Artwork-specific image storage service that composes a generic storage service."""

    def __init__(self, storage_service: StorageService):
        """
        Initialize artwork image storage service.

        Args:
            storage_service: Generic storage service implementation
        """
        self.storage = storage_service
        logger.info("Initialized artwork image storage service")

    async def upload_artwork_image(
        self, artwork_id: str, image_data: bytes, content_type: str
    ) -> str:
        """
        Upload artwork image to storage.

        Args:
            artwork_id: Unique identifier for the artwork
            image_data: Raw image data bytes
            content_type: MIME type of the image

        Returns:
            Storage path where the image was saved
        """
        # Generate artwork-specific path
        path = f"artwork/{artwork_id}"

        try:
            # Upload using generic storage service
            result_path = await self.storage.upload(path, image_data, content_type)
            logger.info(f"Successfully uploaded artwork image: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Error uploading artwork image: {e}")
            raise

    async def get_image_url(
        self,
        image_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> str:
        """
        Generate a public URL for accessing the artwork image.

        Args:
            image_path: Path to the image in storage
            expires_in: URL expiration time in seconds (ignored for public URLs)
            width: Optional width for image transformation
            height: Optional height for image transformation

        Returns:
            Public URL for accessing the image
        """
        try:
            # Generate public URL using generic storage service
            public_url = await self.storage.get_public_url(
                image_path, width, height
            )
            logger.info(f"Generated public URL for artwork image: {image_path}")
            return public_url

        except Exception as e:
            logger.error(f"Error generating public URL for artwork image: {e}")
            raise

    async def delete_artwork_image(self, image_path: str) -> None:
        """
        Delete an artwork image from storage.

        Args:
            image_path: Path to the image in storage
        """
        try:
            # Delete using generic storage service
            await self.storage.delete(image_path)
            logger.info(f"Successfully deleted artwork image: {image_path}")

        except Exception as e:
            logger.error(f"Error deleting artwork image: {e}")
            raise
