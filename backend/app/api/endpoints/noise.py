"""API endpoints for noise segments."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client

from app.api.schemas.noise import NoiseSegmentResponse
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/noise", tags=["noise"])


@router.get("", response_model=List[NoiseSegmentResponse])
async def get_noise_segments(db: Client = Depends(get_db)):
    """Get latest noise segments with dB levels."""
    try:
        db_service = SupabaseService(db)
        noise = await db_service.get_noise_segments()
        return noise
    except Exception as e:
        logger.error(f"Error fetching noise: {e}")
        raise HTTPException(status_code=500, detail=str(e))
