"""
Base protocol for AI services.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class AIService(Protocol):
    """
    Protocol defining the interface for AI artwork interpretation services.
    """

    async def explain_artwork(self, image_data: bytes, cache_name: str) -> str:
        """
        Send image to AI API for art interpretation.

        Args:
            image_data: Processed image bytes
            cache_name: Unique identifier for this cache

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If AI API call fails
        """
        ...

    async def expand_subject(
        self,
        artwork_id: str,
        original_artwork_explanation: str,
        subject: str, 
    ) -> str:
        """
        Expand on a subject/term in the context of the original artwork.
        
        Args:
            artwork_id: The artwork ID to reuse cached image context
            original_artwork_explanation: The original XML interpretation
            subject: The subject to expand on
            
        Returns:
            Clean XML explanation
            
        Raises:
            Exception: If AI API call fails
        """
        ...
