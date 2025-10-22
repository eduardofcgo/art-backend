"""
Dependency injection for AI provider services.
"""

from config.settings import Settings, AIProvider
from services.gemini_service import GeminiService
from services.base import AIService


def get_settings() -> Settings:
    """
    Dependency provider that returns the application settings instance.

    Returns:
        Settings: The application settings instance
    """
    return Settings()


def get_ai_service(settings: Settings) -> AIService:
    """
    Dependency provider that returns the configured AI service instance.

    Configuration (API keys) is injected from Settings into the service instance.
    Services don't load environment variables directly - they receive configuration
    through constructor injection following the Dependency Inversion Principle.

    Args:
        settings: Application settings (injected dependency)

    Returns:
        GeminiService instance implementing the AIService protocol

    Raises:
        ValueError: If an invalid provider is configured
    """
    if settings.AI_PROVIDER == AIProvider.GEMINI:
        return GeminiService(api_key=settings.GOOGLE_API_KEY)
    else:
        raise ValueError(f"Invalid AI provider: {settings.AI_PROVIDER}. Only Gemini is supported.")
