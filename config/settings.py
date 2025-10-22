"""
Application settings and configuration.
"""

import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class AIProvider(str, Enum):
    """Supported AI providers for artwork interpretation."""

    GEMINI = "gemini"


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        """Initialize settings from environment variables."""
        # AI Provider Configuration
        self.AI_PROVIDER: AIProvider = AIProvider(
            os.getenv("AI_PROVIDER", AIProvider.GEMINI).lower()
        )

        # API Keys
        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

        # Database Configuration
        # Defaults to SQLite. For PostgreSQL: postgresql+asyncpg://user:pass@host/db
        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "sqlite+aiosqlite:///./art_backend.db"
        )
        self.DATABASE_FILE_PATH: str = os.getenv(
            "DATABASE_FILE_PATH", "./art_backend.db"
        )
        self.DATABASE_DRIVER_ADAPTER: str = os.getenv(
            "DATABASE_DRIVER_ADAPTER", "aiosqlite"  # Async SQLite driver
        )

        # PostgreSQL Connection Pool Configuration
        self.POSTGRES_MIN_CONNECTIONS: int = int(
            os.getenv("POSTGRES_MIN_CONNECTIONS", "1")
        )
        self.POSTGRES_MAX_CONNECTIONS: int = int(
            os.getenv("POSTGRES_MAX_CONNECTIONS", "10")
        )
        self.POSTGRES_COMMAND_TIMEOUT: int = int(
            os.getenv("POSTGRES_COMMAND_TIMEOUT", "60")
        )

        # Supabase Storage Configuration
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
        self.SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
        self.SUPABASE_BUCKET: str = os.getenv("SUPABASE_BUCKET", "")
        self.SIGNED_URL_EXPIRY: int = int(
            os.getenv("SIGNED_URL_EXPIRY", "3600")
        )  # 1 hour default

        # API Configuration
        self.BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

        # Validate on initialization
        self.validate()

    def validate(self) -> None:
        """Validate that required API keys are present for the selected provider."""
        if self.AI_PROVIDER == AIProvider.GEMINI and not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required when using Gemini provider")

        # Validate Supabase configuration
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required for image storage")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required for image storage")
