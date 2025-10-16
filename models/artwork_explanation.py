"""
Data models for artwork explanation responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ArtworkExplanation:
    """
    Response data for artwork explanation with optional caching information.

    Attributes:
        explanation_xml: The XML interpretation/explanation of the artwork
        cache_id: Optional cache identifier for reusing context in follow-up requests
    """

    explanation_xml: str
    cache_id: Optional[str] = None
