"""
Utility functions for image validation and processing.
"""

import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)


processed_image_content_type = "image/jpeg"


async def validate_and_process_image(image_data: bytes, max_size: int = 2000) -> bytes:
    """
    Validate image and resize if too large.

    Args:
        image_data: Raw image bytes
        max_size: Maximum dimension size (default: 2000px)

    Returns:
        Processed image bytes in JPEG format

    Raises:
        ValueError: If image format is invalid
    """
    logger.info(f"Starting image validation (received {len(image_data)} bytes)")

    try:
        img = Image.open(io.BytesIO(image_data))
        logger.info(
            f"Image opened successfully: format={img.format}, size={img.size}, mode={img.mode}"
        )

        # Convert to RGB if necessary
        if img.mode not in ("RGB", "RGBA"):
            logger.info(f"Converting image from {img.mode} to RGB")
            img = img.convert("RGB")

        # Resize if image is too large (OpenAI has size limits)
        if max(img.size) > max_size:
            original_size = img.size
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Image resized from {original_size} to {new_size}")

        # Convert back to bytes
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85)
        processed_bytes = output.getvalue()
        logger.info(f"Image processed successfully ({len(processed_bytes)} bytes)")
        return processed_bytes
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid image format: {str(e)}")
