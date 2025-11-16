"""
FastAPI dependencies for NeuraCity backend.
Provides dependency injection for database clients and settings.
"""
from supabase import Client
from app.core.config import Settings, get_settings
from app.core.database import get_supabase_client, get_supabase_admin_client
from app.services.supabase_service import SupabaseService


def get_db() -> Client:
    """
    Dependency to get Supabase client for regular operations.

    Returns:
        Client: Supabase client instance
    """
    return get_supabase_client()


def get_admin_db() -> Client:
    """
    Dependency to get Supabase admin client for elevated operations.

    Returns:
        Client: Supabase admin client instance
    """
    return get_supabase_admin_client()


def get_supabase_service() -> SupabaseService:
    """
    Dependency to get SupabaseService instance for database operations.

    Returns:
        SupabaseService: SupabaseService instance
    """
    client = get_supabase_client()
    return SupabaseService(client)


def get_config() -> Settings:
    """
    Dependency to get application settings.

    Returns:
        Settings: Application settings instance
    """
    return get_settings()
