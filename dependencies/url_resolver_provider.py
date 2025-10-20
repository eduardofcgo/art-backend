"""
URL resolver dependency provider.
"""

from litestar import Request
from litestar.di import Provide
from utils.url_resolver import URLResolver


def get_url_resolver(request: Request) -> URLResolver:
    """
    Create and return a URL resolver instance.

    Args:
        request: The Litestar request object

    Returns:
        Configured URL resolver instance
    """
    return URLResolver(request)


# Dependency provider for Litestar
url_resolver_provider = Provide(get_url_resolver, sync_to_thread=False)
