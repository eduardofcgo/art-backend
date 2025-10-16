"""
Artwork storage service dependency provider.
"""

from litestar.di import Provide
from services.storage.object_storage import ObjectStorageService
from services.storage.artwork_image_storage import ArtworkImageStorage
from config.settings import Settings


def get_artwork_storage_service(settings: Settings) -> ArtworkImageStorage:
    """
    Create and return an artwork storage service instance.

    Args:
        settings: Application settings containing storage configuration

    Returns:
        Configured artwork storage service instance
    """
    # Create generic object storage service
    object_storage = ObjectStorageService(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_KEY,
        bucket=settings.SUPABASE_BUCKET,
        signed_url_expiry=settings.SIGNED_URL_EXPIRY,
    )

    # Wrap in artwork-specific service
    return ArtworkImageStorage(object_storage)


# Dependency provider for Litestar
artwork_storage_provider = Provide(get_artwork_storage_service, sync_to_thread=False)
