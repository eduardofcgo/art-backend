"""
Abstract base class for storage services.
"""

from abc import ABC, abstractmethod
from typing import Optional


class StorageService(ABC):
    """Abstract base class for storage operations."""

    @abstractmethod
    async def upload(self, path: str, data: bytes, content_type: str) -> str:
        """
        Upload data to storage and return the storage path.

        Args:
            path: Storage path where the data should be saved
            data: Raw data bytes
            content_type: MIME type of the data (e.g., 'image/jpeg', 'application/pdf')

        Returns:
            Storage path where the data was saved
        """
        pass

    @abstractmethod
    async def generate_signed_url(
        self,
        path: str,
        expires_in: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> str:
        """
        Generate a signed URL for accessing the object.

        Args:
            path: Path to the object in storage
            expires_in: URL expiration time in seconds (uses default if None)
            width: Optional width for image transformation
            height: Optional height for image transformation

        Returns:
            Signed URL for accessing the object
        """
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """
        Delete an object from storage.

        Args:
            path: Path to the object in storage
        """
        pass
