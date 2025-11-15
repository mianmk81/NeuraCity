"""
Configuration module for NeuraCity backend.
Loads and validates all environment variables with proper defaults.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # AI API Keys
    GEMINI_API_KEY: str
    HUGGINGFACE_API_KEY: str = ""  # Optional, for HuggingFace Inference API

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = False

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # File Upload Configuration
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    UPLOAD_DIR: str = "uploads"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "NeuraCity API"
    VERSION: str = "1.0.0"

    # Routing Configuration
    DEFAULT_WALK_SPEED_KMH: float = 5.0
    DEFAULT_DRIVE_SPEED_KMH: float = 50.0

    # AI Model Configuration
    SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Database Query Limits
    MAX_ISSUES_LIMIT: int = 1000
    DEFAULT_ISSUES_LIMIT: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()
