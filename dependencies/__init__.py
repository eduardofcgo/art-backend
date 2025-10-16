"""Dependencies module."""

from dependencies.ai_provider import get_ai_service, get_settings
from dependencies.auth import authenticated_user_provider, AuthenticatedUser

__all__ = [
    "get_ai_service",
    "get_settings",
    "authenticated_user_provider",
    "AuthenticatedUser",
]
