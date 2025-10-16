"""
Simple Optional Authentication Middleware for Litestar.

This middleware provides optional JWT authentication - it will authenticate
requests that have a valid Authorization header, but will allow requests
without the header to pass through without authentication.
"""

import logging
from typing import Optional, Any
from litestar import Request
from litestar.security.jwt import JWTAuthenticationMiddleware
from litestar.middleware.base import DefineMiddleware, AbstractMiddleware
from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from litestar.exceptions import NotAuthorizedException
from litestar.types import ASGIApp, Method, Receive, Scope, Scopes, Send 

logger = logging.getLogger(__name__)


def _retrieve_user(token: Token, connection) -> Optional[str]:
    """Extract user ID from JWT token. Returns None if no token or invalid token."""
    
    user_id = token.sub if token.sub else None

    # The return value is automatically made available as request.user
    return user_id


class AuthMiddleware(JWTAuthenticationMiddleware):
    """
    Middleware that provides JWT authentication.
    """
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    async def __call__(self, scope: Scope, receive, send: Send) -> None:
        connection = ASGIConnection(scope, receive, send)
        auth_header = connection.headers.get(self.auth_header)

        if not auth_header:
            # No auth header provided, set user to None and continue to the app
            scope["user"] = None
            await self.app(scope, receive, send)
        else:
            # Auth header exists, use parent class authentication
            await super().__call__(scope, receive, send)


def create_auth(**kwargs):
    return JWTAuth[Optional[str]](
        **kwargs,
        retrieve_user_handler=_retrieve_user,
        authentication_middleware_class=AuthMiddleware,
    )