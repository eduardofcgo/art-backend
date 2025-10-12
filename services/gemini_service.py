"""
Service layer for Google Gemini API integration.
"""

import io
import logging
from typing import Optional
from PIL import Image
from google import genai
from google.genai import types
from config.prompts import ART_EXPLANATION_PROMPT, WIKILINK_EXPANSION_PROMPT
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
        self.generation_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        )
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
        self.cache_ttl = "3600s"  # 60 minutes in seconds

    async def explain_artwork(self, image_data: bytes, cache_name: str):
        """
        Send image to Gemini API with context caching enabled when possible.
        Falls back to regular API call if content is too small for caching.

        Args:
            image_data: Processed image bytes
            cache_name: Unique identifier for this cache (e.g., session ID or UUID)

        Returns:
            Clean XML interpretation (guaranteed to be properly formatted)

        Raises:
            Exception: If Gemini API call fails
        """
        logger.info(f"Starting Gemini API request with caching (cache_name={cache_name})")

        try:
            # Upload image to Gemini Files API
            image_io = io.BytesIO(image_data)
            image_file = self.client.files.upload(
                file=image_io,
                config=dict(mime_type='image/jpeg')
            )
            logger.info(f"Image uploaded: {image_file.name}, size={len(image_data)} bytes")

            # Try to create cached content with the image and system instruction
            # This will be reused for follow-up questions if successful
            try:
                cache = self.client.caches.create(
                    model=self.model_name,
                    config=types.CreateCachedContentConfig(
                        display_name=cache_name,
                        system_instruction=ART_EXPLANATION_PROMPT,
                        contents=[image_file],
                        ttl=self.cache_ttl,
                    )
                )
                logger.info(f"Created context cache: {cache.name}")
                logger.info(f"Cache model: {cache.model}, expires: {cache.expire_time}")
                logger.info(f"Cached tokens: {cache.usage_metadata}")

                # Generate response using the cached content
                logger.info("Sending request to Gemini API with cached context...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents="Please analyze this artwork according to your instructions.",
                    config=types.GenerateContentConfig(
                        cached_content=cache.name,
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=8192,
                        safety_settings=self.safety_settings,
                    )
                )
                
            except Exception as cache_error:
                # If caching fails (e.g., content too small - min 4096 tokens required),
                # fall back to regular API call without caching
                error_msg = str(cache_error)
                if "too small" in error_msg.lower() or "min_total_token_count" in error_msg.lower():
                    logger.warning(f"Content too small for caching (min 4096 tokens required), using regular API call: {error_msg}")
                else:
                    logger.warning(f"Caching failed, falling back to regular API call: {error_msg}")
                
                # Make regular API call without caching
                logger.info("Sending request to Gemini API without caching...")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        ART_EXPLANATION_PROMPT,
                        image_file,
                        "Please analyze this artwork according to the instructions above."
                    ],
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=8192,
                        safety_settings=self.safety_settings,
                    )
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

    async def expand_subject(
        self, 
        artwork_id: str,
        original_artwork_explanation: str,
        subject: str, 
    ) -> str:
        """
        Expand on a subject/term in the context of the original artwork using cached image/context.

        Args:
            artwork_id: The cache name/ID to reuse cached image context
            original_artwork_explanation: The original artwork explanation
            subject: The subject to expand on

        Returns:
            Clean XML explanation

        Raises:
            Exception: If Gemini API call fails
        """
        logger.info(f"Expanding subject '{subject}' with cached context (artwork_id={artwork_id})")

        try:
            # Get the cached content by name
            cache = self.client.caches.get(name=artwork_id)
            logger.info(f"Retrieved cache: {cache.name}, expires: {cache.expire_time}")
            
            # Generate expanded explanation using cached context
            prompt = WIKILINK_EXPANSION_PROMPT.format(
                subject=subject,
                original_explanation=original_artwork_explanation
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    cached_content=cache.name,
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=8192,
                    safety_settings=self.safety_settings,
                )
            )
            logger.info(f"Received expansion response, usage: {response.usage_metadata}")
            
            raw_content = response.text
            cleaned_xml = clean_xml_response(raw_content)
            return cleaned_xml
            
        except Exception as e:
            logger.error(f"Error expanding subject with caching: {str(e)}", exc_info=True)
            raise
        