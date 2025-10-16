"""
Exception handlers for centralized error handling.

These handlers integrate with Litestar's native exception handling system.
Litestar automatically logs exceptions with full tracebacks before calling these handlers.
"""

import logging
from litestar import Request, Response
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.exceptions import NotAuthorizedException

logger = logging.getLogger(__name__)


def value_error_handler(request: Request, exc: ValueError) -> Response:
    """
    Handle ValueError exceptions (validation errors) and return XML error response.

    Litestar will automatically log this exception with full traceback before
    calling this handler.

    Args:
        request: The request that caused the exception
        exc: The ValueError exception

    Returns:
        Response with XML error message and 400 status code
    """
    error_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
    <status>error</status>
    <message>{str(exc)}</message>
</error>"""
    return Response(
        content=error_xml,
        media_type="application/xml",
        status_code=HTTP_400_BAD_REQUEST,
    )


def not_authorized_handler(request: Request, exc: NotAuthorizedException) -> Response:
    """
    Handle NotAuthorizedException and return XML error response.

    This handler specifically catches JWT authentication errors and returns
    a proper 401 response instead of letting it fall through to the generic handler.

    Args:
        request: The request that caused the exception
        exc: The NotAuthorizedException

    Returns:
        Response with XML error message and 401 status code
    """
    error_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
    <status>error</status>
    <message>Authentication required: {str(exc)}</message>
</error>"""
    return Response(
        content=error_xml,
        media_type="application/xml",
        status_code=401,
    )


def generic_exception_handler(request: Request, exc: Exception) -> Response:
    """
    Handle all other exceptions and return XML error response.

    Litestar will automatically log this exception with full traceback before
    calling this handler.

    Args:
        request: The request that caused the exception
        exc: The exception

    Returns:
        Response with XML error message and 500 status code
    """
    error_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<error>
    <status>error</status>
    <message>An error occurred while processing the request: {str(exc)}</message>
</error>"""
    return Response(
        content=error_xml,
        media_type="application/xml",
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
