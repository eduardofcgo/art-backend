"""
Authentication dependencies for dependency injection.
"""

from typing import Optional
from dataclasses import dataclass
from litestar import Request
from litestar.di import Provide
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuthenticatedUser:
    """Represents an authenticated user from JWT token."""

    id: str

    def __post_init__(self):
        """Validate that ID is not null."""
        if not self.id:
            raise ValueError("AuthenticatedUser must have a valid ID")


async def get_authenticated_user(request: Request) -> Optional[AuthenticatedUser]:
    """
    Dependency provider that extracts the authenticated user from the request.

    The JWT middleware sets request.user to the user ID (sub claim from token).
    This dependency wraps it in an AuthenticatedUser object for cleaner access.

    Returns:
        AuthenticatedUser if user is authenticated, None otherwise.
    """
    user_id = request.user if hasattr(request, "user") else None

    logger.debug(
        f"🔐 Auth Dependency: Extracting user from request - user_id: {user_id}"
    )

    # Only create AuthenticatedUser if we have a valid user ID
    if user_id:
        return AuthenticatedUser(id=user_id)

    return None


# Export the provider for use in dependency injection
authenticated_user_provider = Provide(get_authenticated_user, sync_to_thread=False)
