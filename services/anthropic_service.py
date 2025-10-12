"""
Service layer for Anthropic Claude API integration.
"""

import base64
import logging
from typing import Optional
from anthropic import Anthropic
from config.prompts import ART_EXPLANATION_PROMPT, WIKILINK_EXPANSION_USER_MESSAGE
from utils.response_cleaner import clean_xml_response
from models import ArtworkExplanation

logger = logging.getLogger(__name__)


class AnthropicService:
    """Anthropic Claude service for artwork interpretation."""

    def __init__(self, api_key: str):
        """
        Initialize Anthropic service with API key.

        Args:
            api_key: Anthropic API key
        """
        self.client = Anthropic(api_key=api_key)
        logger.info("Anthropic service initialized")

    async def explain_artwork(self, image_data: bytes) -> str:
        """
        Send image to Anthropic Claude API for art interpretation.

        Args:
            image_data: Processed image bytes

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If Anthropic API call fails
        """
        logger.info("Starting Anthropic API request for artwork interpretation")

        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            logger.debug("Image encoded to base64")

            # Call Anthropic Claude API
            logger.info("Sending request to Anthropic API...")
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet for high-quality vision analysis
                max_tokens=8192,  # Increased for more in-depth explanations exploring multiple topics
                temperature=0.7,  # Match other services for consistent creativity level
                system=ART_EXPLANATION_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Please analyze this artwork according to your instructions.",
                            },
                        ],
                    }
                ],
            )
            logger.info("Received response from Anthropic API")

            raw_content = response.content[0].text
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML response cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(f"Error in Anthropic API call: {str(e)}", exc_info=True)
            raise

    async def interpret_artwork_with_cache(self, image_data: bytes, cache_name: str) -> ArtworkExplanation:
        """
        Anthropic supports prompt caching but implementation is more complex.
        For now, fall back to regular interpretation.
        
        TODO: Implement Anthropic's prompt caching feature.
        """
        logger.info("Anthropic: Using regular interpretation (caching not yet implemented)")
        interpretation = await self.explain_artwork(image_data)
        return ArtworkExplanation(
            explanation_xml=interpretation,
            cache_id=cache_name
        )

    async def expand_subject(
        self,
        artwork_id: str,
        original_artwork_explanation: str,
        subject: str,
    ) -> str:
        """
        Expand on a subject/term using text-only context.
        """
        logger.info(f"Anthropic: Expanding subject '{subject}' with text-only context")
        
        try:
            # Create a fake conversation where the AI already provided the original analysis
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                temperature=0.7,
                system=ART_EXPLANATION_PROMPT,
                messages=[
                    {"role": "user", "content": "Please analyze this artwork."},
                    {"role": "assistant", "content": original_artwork_explanation},
                    {"role": "user", "content": WIKILINK_EXPANSION_USER_MESSAGE.format(subject=subject)},
                ],
            )
            logger.info("Received explanation response from Anthropic API")
            
            raw_content = response.content[0].text
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML explanation cleaned and validated")
            return cleaned_xml
            
        except Exception as e:
            logger.error(f"Error explaining term with Anthropic: {str(e)}", exc_info=True)
            raise
