"""
Service layer for OpenAI API integration.
"""

import base64
import logging
from typing import Optional
from openai import OpenAI
from config.prompts import ART_EXPLANATION_PROMPT, WIKILINK_EXPANSION_PROMPT
from utils.response_cleaner import clean_xml_response
from models import ArtworkExplanation

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for artwork interpretation."""

    def __init__(self, api_key: str):
        """
        Initialize OpenAI service with API key.

        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAI service initialized")

    async def explain_artwork(self, image_data: bytes) -> str:
        """
        Send image to OpenAI Vision API for art interpretation.

        Args:
            image_data: Processed image bytes

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If OpenAI API call fails
        """
        logger.info("Starting OpenAI API request for artwork interpretation")

        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            logger.debug("Image encoded to base64")

            # Call OpenAI Vision API
            logger.info("Sending request to OpenAI API...")
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o which has vision capabilities
                messages=[
                    {"role": "system", "content": ART_EXPLANATION_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this artwork according to your instructions.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                temperature=0.7,  # Match Gemini's temperature for consistent creativity level
                max_tokens=8192,  # Increased for more in-depth explanations exploring multiple topics
            )
            logger.info("Received response from OpenAI API")

            raw_content = response.choices[0].message.content
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML response cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
            raise

    async def interpret_artwork_with_cache(self, image_data: bytes, cache_name: str) -> ArtworkExplanation:
        """
        OpenAI doesn't support explicit caching in the same way as Gemini.
        Fall back to regular interpretation.
        
        Note: OpenAI does have automatic prompt caching for prompts >1024 tokens,
        but it's automatic and doesn't provide cache IDs for reuse.
        """
        logger.info("OpenAI: Using regular interpretation (automatic caching may apply)")
        interpretation = await self.explain_artwork(image_data)
        return ArtworkExplanation(
            explanation_xml=interpretation,
            cache_id=cache_name
        )

    async def expand_subject(
        self,
        term: str,
        original_interpretation: str,
        cache_name: Optional[str] = None
    ) -> str:
        """
        Expand on a subject/term using text-only context (OpenAI doesn't support explicit cache reuse).
        """
        logger.info(f"OpenAI: Expanding subject '{term}' with text-only context")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": WIKILINK_EXPANSION_PROMPT},
                    {
                        "role": "user",
                        "content": f"""Original Artwork Analysis:
{original_interpretation}

Term to explain: {term}

Please provide an in-depth explanation of this term specifically in the context of the artwork described in the analysis above."""
                    },
                ],
                temperature=0.7,
                max_tokens=4096,
            )
            logger.info("Received explanation response from OpenAI API")
            
            raw_content = response.choices[0].message.content
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML explanation cleaned and validated")
            return cleaned_xml
            
        except Exception as e:
            logger.error(f"Error explaining term with OpenAI: {str(e)}", exc_info=True)
            raise
