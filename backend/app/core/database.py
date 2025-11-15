"""
Database module for NeuraCity backend.
Initializes and manages Supabase client connection.
"""
from supabase import create_client, Client
from functools import lru_cache
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.

    Returns:
        Client: Initialized Supabase client

    Raises:
        Exception: If Supabase client initialization fails
    """
    settings = get_settings()

    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        logger.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise


@lru_cache()
def get_supabase_admin_client() -> Client:
    """
    Get cached Supabase admin client with service role key.
    Used for operations that require elevated permissions.

    Returns:
        Client: Initialized Supabase admin client

    Raises:
        Exception: If Supabase admin client initialization fails
    """
    settings = get_settings()

    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_KEY
        )
        logger.info("Supabase admin client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {str(e)}")
        raise
