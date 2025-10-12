"""
Application settings and configuration.
"""

import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class AIProvider(str, Enum):
    """Supported AI providers for artwork interpretation."""

    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # AI Provider Configuration
        self.AI_PROVIDER: AIProvider = AIProvider(
            os.getenv("AI_PROVIDER", AIProvider.GEMINI).lower()
        )

        # API Keys
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

        # Validate on initialization
        self.validate()

    def validate(self) -> None:
        """Validate that required API keys are present for the selected provider."""
        if self.AI_PROVIDER == AIProvider.OPENAI and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        elif self.AI_PROVIDER == AIProvider.GEMINI and not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")
        elif self.AI_PROVIDER == AIProvider.ANTHROPIC and not self.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Anthropic provider"
            )
