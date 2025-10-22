"""
Service layer for OpenAI API integration.
"""

import base64
import io
import logging
from typing import Optional
from PIL import Image
from openai import AsyncOpenAI
from config.prompts import ART_EXPLANATION_PROMPT, WIKILINK_EXPANSION_USER_MESSAGE
from utils.response_cleaner import clean_xml_response

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for artwork interpretation."""

    def __init__(self, api_key: str):
        """
        Initialize OpenAI service with API key.

        Args:
            api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=60.0,  # 60 second timeout
        )
        self.model_name = "gpt-4o-mini"  # Cheapest vision-capable model
        self.temperature = 0.7
        self.max_tokens = 4096

    async def explain_artwork(self, image_data: bytes, cache_name: str):
        """
        Send image to OpenAI API for art interpretation.

        Args:
            image_data: Processed image bytes
            cache_name: Unique identifier (not used, kept for API compatibility)

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If OpenAI API call fails
        """
        logger.info(f"Starting OpenAI API request without caching")

        try:
            # Convert image bytes to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Make API call to OpenAI
            logger.info("Sending request to OpenAI API...")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": ART_EXPLANATION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this artwork."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            logger.info("Received response from OpenAI API")
            logger.info(f"Usage: {response.usage}")

            raw_content = response.choices[0].message.content
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML response cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
            raise

    async def explain_artwork_by_name(self, artwork_name: str, cache_name: str) -> str:
        """
        Send artwork name to OpenAI API for art interpretation.

        Args:
            artwork_name: Name of the artwork to analyze
            cache_name: Unique identifier for this cache

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If OpenAI API call fails
        """
        logger.info(f"Starting OpenAI API request for artwork interpretation by name: {artwork_name}")

        try:
            # Call OpenAI API with artwork name
            logger.info("Sending request to OpenAI API...")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": ART_EXPLANATION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Please analyze the artwork '{artwork_name}' according to your instructions."
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            logger.info("Received response from OpenAI API")
            logger.info(f"Usage: {response.usage}")

            raw_content = response.choices[0].message.content
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML response cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(f"Error in OpenAI API call for artwork by name: {str(e)}", exc_info=True)
            raise

    async def expand_subject(
        self,
        artwork_id: str,
        original_artwork_explanation: str,
        subject: str,
    ) -> str:
        """
        Expand on a subject/term in the context of the original artwork.

        Args:
            artwork_id: The artwork ID (not used for now, reserved for future caching)
            original_artwork_explanation: The original artwork explanation
            subject: The subject to expand on

        Returns:
            Clean XML explanation

        Raises:
            Exception: If OpenAI API call fails
        """
        logger.info(f"OpenAI: Expanding subject '{subject}' with text-only context")

        try:
            # Create a conversation history where the AI already provided the original analysis
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": ART_EXPLANATION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": "Please analyze this artwork."
                    },
                    {
                        "role": "assistant",
                        "content": original_artwork_explanation
                    },
                    {
                        "role": "user",
                        "content": WIKILINK_EXPANSION_USER_MESSAGE.format(subject=subject)
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            logger.info("Received response from OpenAI API")
            logger.info(f"Usage: {response.usage}")

            raw_content = response.choices[0].message.content
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML explanation cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(
                f"Error expanding subject with OpenAI: {str(e)}", exc_info=True
            )
            raise
