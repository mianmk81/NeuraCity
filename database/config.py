"""
NeuraCity Database Configuration

Loads configuration from environment variables with validation.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration from environment variables"""

    def __init__(self):
        self.supabase_url: str = os.getenv('SUPABASE_URL', '')
        self.supabase_key: str = os.getenv('SUPABASE_KEY', '')
        self.supabase_service_role_key: Optional[str] = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    def validate(self) -> tuple[bool, str]:
        """
        Validate that all required configuration is present

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.supabase_url:
            return False, "SUPABASE_URL is not set in environment"

        if not self.supabase_key:
            return False, "SUPABASE_KEY is not set in environment"

        if not self.supabase_url.startswith('https://'):
            return False, "SUPABASE_URL must start with https://"

        return True, ""

    def __repr__(self) -> str:
        return f"DatabaseConfig(url={self.supabase_url[:30]}..., key={'***' if self.supabase_key else 'NOT SET'})"


def get_config() -> DatabaseConfig:
    """
    Get validated database configuration

    Raises:
        ValueError: If configuration is invalid
    """
    config = DatabaseConfig()
    is_valid, error_msg = config.validate()

    if not is_valid:
        raise ValueError(
            f"Invalid database configuration: {error_msg}\n"
            "Please check your .env file and ensure all required variables are set.\n"
            "Copy .env.example to .env and fill in your Supabase credentials."
        )

    return config


if __name__ == '__main__':
    # Test configuration loading
    try:
        config = get_config()
        print("✓ Configuration loaded successfully")
        print(config)
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
