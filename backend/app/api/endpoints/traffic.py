"""API endpoints for traffic segments."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client

from app.api.schemas.traffic import TrafficSegmentResponse
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/traffic", tags=["traffic"])


@router.get("", response_model=List[TrafficSegmentResponse])
async def get_traffic_segments(db: Client = Depends(get_db)):
    """Get latest traffic segments with congestion data."""
    try:
        db_service = SupabaseService(db)
        traffic = await db_service.get_traffic_segments()
        return traffic
    except Exception as e:
        logger.error(f"Error fetching traffic: {e}")
        raise HTTPException(status_code=500, detail=str(e))
