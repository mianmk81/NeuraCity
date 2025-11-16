"""API endpoints for user management and gamification."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from supabase import Client

from app.api.schemas.user import (
    UserCreate, UserUpdate, UserResponse, LeaderboardResponse,
    LeaderboardEntry, PointsHistoryResponse
)
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
from app.services.gamification_service import GamificationService
from app.utils.cache import cached_response, LEADERBOARD_CACHE, invalidate_cache
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: Client = Depends(get_db)
):
    """
    Create a new user for the gamification system.

    Args:
        user_data: User creation data (username, email, full_name, avatar_url)

    Returns:
        Created user with gamification fields initialized
    """
    try:
        db_service = SupabaseService(db)

        # Check if username already exists
        existing_username = await db_service.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Check if email already exists
        existing_email = await db_service.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Create user with initial gamification values
        user_dict = user_data.model_dump()
        user_dict.update({
            "total_points": 0,
            "rank": 0,
            "issues_reported": 0,
            "issues_verified": 0
        })

        created_user = await db_service.create_user(user_dict)

        # Invalidate leaderboard cache
        invalidate_cache(LEADERBOARD_CACHE)

        logger.info(f"Created user {created_user['id']} with username {user_data.username}")
        return created_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Client = Depends(get_db)
):
    """
    Get user profile with gamification data.

    Args:
        user_id: User UUID

    Returns:
        User profile with points, rank, and statistics
    """
    try:
        db_service = SupabaseService(db)
        user = await db_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    db: Client = Depends(get_db)
):
    """
    Update user profile (non-gamification fields only).

    Args:
        user_id: User UUID
        update_data: Fields to update (full_name, avatar_url)

    Returns:
        Updated user profile
    """
    try:
        db_service = SupabaseService(db)

        existing = await db_service.get_user_by_id(user_id)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            raise HTTPException(status_code=400, detail="No update data provided")

        updated = await db_service.update_user(user_id, update_dict)

        logger.info(f"Updated user {user_id}")
        return updated

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/points-history", response_model=List[PointsHistoryResponse])
async def get_user_points_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    db: Client = Depends(get_db)
):
    """
    Get user's points transaction history.

    Args:
        user_id: User UUID
        limit: Maximum number of records (default 50, max 100)

    Returns:
        List of points history entries
    """
    try:
        db_service = SupabaseService(db)

        # Verify user exists
        user = await db_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        history = await db_service.get_user_points_history(user_id, limit=limit)

        return history

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching points history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    db: Client = Depends(get_db)
):
    """
    Get paginated leaderboard of users sorted by points.

    Args:
        page: Page number (default 1)
        page_size: Results per page (default 10, max 100)

    Returns:
        Paginated leaderboard with user rankings
    """
    async def _get_leaderboard(page: int, page_size: int):
        db_service = SupabaseService(db)

        # Get total count
        total = await db_service.get_total_user_count()

        # Get paginated leaderboard
        offset = (page - 1) * page_size
        entries = await db_service.get_leaderboard(limit=page_size, offset=offset)

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "entries": entries
        }

    try:
        # Use cached version
        @cached_response(LEADERBOARD_CACHE, "leaderboard")
        async def cached_leaderboard(p: int, ps: int):
            return await _get_leaderboard(p, ps)

        result = await cached_leaderboard(page, page_size)
        return result

    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
