"""
Domain models for artwork records.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ArtworkRecord:
    """
    Domain model for an artwork explanation record.

    Attributes:
        artwork_id: Unique identifier for the artwork
        explanation_xml: The XML interpretation/explanation of the artwork
        image_path: Path to the image in Supabase Storage (optional)
        creator_user_id: User who created/uploaded the artwork (optional for anonymous)
        created_at: Timestamp when the record was created
    """

    artwork_id: str
    explanation_xml: str
    image_path: Optional[str]
    creator_user_id: Optional[str]
    created_at: datetime


@dataclass
class SubjectExpansionRecord:
    """
    Domain model for a subject expansion record.

    Attributes:
        expansion_id: Unique identifier for this expansion
        artwork_id: Reference to the original artwork
        subject: The subject that was expanded on
        subject_hash: SHA-256 hash of the subject for efficient caching
        expansion_xml: The XML expansion of the subject
        parent_expansion_id: Reference to parent expansion (None for root expansions)
        created_at: Timestamp when the record was created
    """

    expansion_id: str
    artwork_id: str
    subject: str
    subject_hash: str
    expansion_xml: str
    parent_expansion_id: Optional[str]
    created_at: datetime
