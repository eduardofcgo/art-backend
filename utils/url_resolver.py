"""
URL resolver utility for generating URLs with both path parameters and query parameters.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode
from litestar import Request


class URLResolver:
    """
    URL resolver that wraps request.url_for() and supports query parameters.
    """
    
    def __init__(self, request: Request):
        """
        Initialize the URL resolver with a request object.
        
        Args:
            request: The Litestar request object
        """
        self.request = request
    
    def resolve_url(
        self, 
        route_name: str, 
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Resolve a URL for a route with both path parameters and query parameters.
        
        Args:
            route_name: The name of the route to resolve
            path_params: Dictionary of path parameters for the route
            query_params: Dictionary of query parameters to append
            
        Returns:
            The complete URL with query string if query_params provided
            
        Example:
            url_resolver.resolve_url(
                "get_artwork_image",
                path_params={"artwork_id": "123"},
                query_params={"size": "sm"}
            )
            # Returns: "/artwork/123/image?size=sm"
        """
        # Use path_params if provided, otherwise empty dict
        params = path_params or {}
        
        # Generate the base URL using request.url_for()
        base_url = self.request.url_for(route_name, **params)
        
        # Append query parameters if provided
        if query_params:
            query_string = urlencode(query_params)
            return f"{base_url}?{query_string}"
        
        return base_url
