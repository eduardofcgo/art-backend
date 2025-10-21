"""
Generic object storage implementation.
"""

import logging
from typing import Optional
from supabase import create_client, Client
from services.storage.base import StorageService

logger = logging.getLogger(__name__)


class ObjectStorageService(StorageService):
    """Generic object storage implementation."""

    def __init__(self, url: str, key: str, bucket: str, signed_url_expiry: int):
        """
        Initialize object storage service.

        Args:
            url: Storage service URL
            key: API key
            bucket: Storage bucket name
            signed_url_expiry: Default expiration time for signed URLs in seconds
        """
        self.client: Client = create_client(url, key)
        self.bucket = bucket
        self.signed_url_expiry = signed_url_expiry
        logger.info(f"Initialized object storage service with bucket: {bucket}")

    async def upload(self, path: str, data: bytes, content_type: str) -> str:
        """
        Upload data to storage.

        Args:
            path: Storage path where the data should be saved
            data: Raw data bytes
            content_type: MIME type of the data

        Returns:
            Storage path where the data was saved
        """
        try:
            # Upload to storage
            result = self.client.storage.from_(self.bucket).upload(
                path=path, file=data, file_options={"content-type": content_type}
            )

            logger.info(f"Successfully uploaded data to storage: {path}")
            return path

        except Exception as e:
            logger.error(f"Error uploading data to storage: {e}")
            raise

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
        if expires_in is None:
            expires_in = self.signed_url_expiry

        try:
            # Prepare transform options if width or height are provided
            options = {}
            if width is not None or height is not None:
                transform_options = {}
                if width is not None:
                    transform_options["width"] = width
                if height is not None:
                    transform_options["height"] = height
                options["transform"] = transform_options

            # Generate signed URL
            result = self.client.storage.from_(self.bucket).create_signed_url(
                path, expires_in, options
            )

            # Check if signed URL generation was successful
            if hasattr(result, "get") and result.get("error"):
                raise Exception(f"Failed to create signed URL: {result['error']}")
            elif hasattr(result, "error") and result.error:
                raise Exception(f"Failed to create signed URL: {result.error}")

            # Extract signed URL from result
            signed_url = None
            if hasattr(result, "get"):
                signed_url = result.get("signedURL")
            elif hasattr(result, "signedURL"):
                signed_url = result.signedURL
            elif hasattr(result, "signed_url"):
                signed_url = result.signed_url

            if not signed_url:
                raise Exception("No signed URL returned from storage service")

            logger.info(f"Generated signed URL for object: {path}")
            return signed_url

        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            raise

    async def get_public_url(
        self,
        path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> str:
        """
        Get a public URL for accessing the object.

        Args:
            path: Path to the object in storage
            width: Optional width for image transformation
            height: Optional height for image transformation

        Returns:
            Public URL for accessing the object
        """
        try:
            # Get the public URL from Supabase storage
            public_url = self.client.storage.from_(self.bucket).get_public_url(path)
            
            # Add transformation parameters if width or height are provided
            if width is not None or height is not None:
                transform_params = []
                if width is not None:
                    transform_params.append(f"width={width}")
                if height is not None:
                    transform_params.append(f"height={height}")
                
                if transform_params:
                    separator = "&" if "?" in public_url else "?"
                    public_url += f"{separator}{'&'.join(transform_params)}"

            logger.info(f"Generated public URL for object: {path}")
            return public_url

        except Exception as e:
            logger.error(f"Error generating public URL: {e}")
            raise

    async def delete(self, path: str) -> None:
        """
        Delete an object from storage.

        Args:
            path: Path to the object in storage
        """
        try:
            # Delete from storage
            result = self.client.storage.from_(self.bucket).remove([path])

            # Check if deletion was successful
            if hasattr(result, "get") and result.get("error"):
                raise Exception(f"Failed to delete object: {result['error']}")
            elif hasattr(result, "error") and result.error:
                raise Exception(f"Failed to delete object: {result.error}")

            logger.info(f"Successfully deleted object from storage: {path}")

        except Exception as e:
            logger.error(f"Error deleting object from storage: {e}")
            raise
