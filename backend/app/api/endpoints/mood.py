"""API endpoints for mood areas."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client

from app.api.schemas.mood import MoodAreaResponse
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mood", tags=["mood"])


@router.get("", response_model=List[MoodAreaResponse])
async def get_mood_areas(db: Client = Depends(get_db)):
    """Get all mood areas with sentiment scores."""
    try:
        db_service = SupabaseService(db)
        mood_areas = await db_service.get_mood_areas()
        return mood_areas
    except Exception as e:
        logger.error(f"Error fetching mood areas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
