"""
Service layer for Google Gemini API integration.
"""

import io
import logging
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types
from config.prompts import ART_EXPLANATION_PROMPT, WIKILINK_EXPANSION_USER_MESSAGE
from utils.response_cleaner import clean_xml_response
from models import ArtworkExplanation

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini service for artwork interpretation."""

    def __init__(self, api_key: str):
        """
        Initialize Gemini service with API key.

        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = "models/gemini-2.0-flash-001"
        self.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_NONE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_NONE"
            ),
        ]
        self.generation_config = types.GenerateContentConfig(
            system_instruction=ART_EXPLANATION_PROMPT,
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=4096,
            safety_settings=self.safety_settings,
        )
        self.cache_ttl = "3600s"  # 60 minutes in seconds

    async def explain_artwork(self, image_data: bytes, cache_name: str):
        """
        Send image to Gemini API without caching.

        Args:
            image_data: Processed image bytes
            cache_name: Unique identifier (not used, kept for API compatibility)

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If Gemini API call fails
        """
        logger.info(f"Starting Gemini API request without caching")

        try:
            # Upload image to Gemini Files API
            image_io = io.BytesIO(image_data)
            image_file = self.client.files.upload(
                file=image_io,
                config=dict(mime_type='image/jpeg')
            )
            logger.info(f"Image uploaded: {image_file.name}, size={len(image_data)} bytes")

            # Make regular API call without caching
            logger.info("Sending request to Gemini API...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(file_uri=image_file.uri, mime_type=image_file.mime_type),
                        types.Part.from_text(text="Please analyze this artwork.")
                    ]
                ),
                config=self.generation_config,
            )
            
            logger.info("Received response from Gemini API")
            logger.info(f"Usage: {response.usage_metadata}")

            raw_content = response.text
            logger.debug(f"Raw response length: {len(raw_content)} characters")

            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML response cleaned and validated")
            return cleaned_xml

        except Exception as e:
            logger.error(f"Error in Gemini API call: {str(e)}", exc_info=True)
            raise

    # For now we ignore the cache and rebuild the context/conversation
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
            Exception: If Gemini API call fails
        """
        logger.info(f"Gemini: Expanding subject '{subject}' with text-only context")
        
        try:
            # Create a conversation history where the AI already provided the original analysis
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text="Please analyze this artwork.")]
                    ),
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=original_artwork_explanation)]
                    ),
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=WIKILINK_EXPANSION_USER_MESSAGE.format(subject=subject))]
                    )
                ],
                config=self.generation_config,
            )
            logger.info("Received response from Gemini API")
            logger.info(f"Usage: {response.usage_metadata}")
            
            raw_content = response.text
            logger.debug(f"Raw response length: {len(raw_content)} characters")
            
            # Clean and return the XML response
            cleaned_xml = clean_xml_response(raw_content)
            logger.info("XML explanation cleaned and validated")
            return cleaned_xml
            
        except Exception as e:
            logger.error(f"Error expanding subject with Gemini: {str(e)}", exc_info=True)
            raise
