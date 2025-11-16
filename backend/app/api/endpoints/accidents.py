"""API endpoints for accident history and analysis."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from supabase import Client

from app.api.schemas.accident import (
    AccidentHistoryResponse, AccidentHotspotsResponse
)
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
from app.services.accident_history_service import AccidentHistoryService
from app.utils.cache import cached_response, ACCIDENT_HISTORY_CACHE
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accidents", tags=["accidents"])


@router.get("/history", response_model=AccidentHistoryResponse)
async def get_accident_history(
    start_date: Optional[datetime] = Query(None, description="Filter accidents after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter accidents before this date"),
    min_lat: Optional[float] = Query(None, ge=-90, le=90, description="Minimum latitude for bounding box"),
    max_lat: Optional[float] = Query(None, ge=-90, le=90, description="Maximum latitude for bounding box"),
    min_lng: Optional[float] = Query(None, ge=-180, le=180, description="Minimum longitude for bounding box"),
    max_lng: Optional[float] = Query(None, ge=-180, le=180, description="Maximum longitude for bounding box"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Client = Depends(get_db)
):
    """
    Get historical accident data with optional filtering.

    Supports filtering by:
    - Date range (start_date, end_date)
    - Geographic bounding box (min_lat, max_lat, min_lng, max_lng)

    Returns paginated results sorted by most recent first.

    Args:
        start_date: Filter accidents after this datetime
        end_date: Filter accidents before this datetime
        min_lat: Minimum latitude for bounding box filter
        max_lat: Maximum latitude for bounding box filter
        min_lng: Minimum longitude for bounding box filter
        max_lng: Maximum longitude for bounding box filter
        page: Page number (default 1)
        page_size: Results per page (default 20, max 100)

    Returns:
        Paginated accident history with total count
    """
    async def _get_history():
        db_service = SupabaseService(db)
        accident_service = AccidentHistoryService(db_service)

        result = await accident_service.get_accident_history(
            start_date=start_date,
            end_date=end_date,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            page=page,
            page_size=page_size
        )

        return result

    try:
        # Use caching for frequently accessed queries
        @cached_response(ACCIDENT_HISTORY_CACHE, "accident_history")
        async def cached_history(sd, ed, minlat, maxlat, minlng, maxlng, p, ps):
            return await _get_history()

        result = await cached_history(
            start_date, end_date, min_lat, max_lat, min_lng, max_lng, page, page_size
        )

        return result

    except Exception as e:
        logger.error(f"Error fetching accident history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hotspots", response_model=AccidentHotspotsResponse)
async def get_accident_hotspots(
    min_accidents: int = Query(2, ge=2, le=10, description="Minimum number of accidents to qualify as hotspot"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of hotspots to return"),
    db: Client = Depends(get_db)
):
    """
    Get geographic areas with multiple accidents (hotspots).

    Identifies locations where multiple accidents have occurred by grouping
    nearby accidents (rounded to 3 decimal places, ~110m precision).

    Args:
        min_accidents: Minimum number of accidents to qualify as hotspot (default 2, max 10)
        limit: Maximum number of hotspots to return (default 50, max 100)

    Returns:
        List of accident hotspots with counts and average severity/urgency
    """
    async def _get_hotspots():
        db_service = SupabaseService(db)
        accident_service = AccidentHistoryService(db_service)

        result = await accident_service.get_accident_hotspots(
            min_accidents=min_accidents,
            limit=limit
        )

        return result

    try:
        # Cache hotspot data
        @cached_response(ACCIDENT_HISTORY_CACHE, "accident_hotspots")
        async def cached_hotspots(min_acc, lim):
            return await _get_hotspots()

        result = await cached_hotspots(min_accidents, limit)

        return result

    except Exception as e:
        logger.error(f"Error fetching accident hotspots: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_accident_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    db: Client = Depends(get_db)
):
    """
    Get statistical summary of accidents.

    Provides aggregate statistics including:
    - Total count
    - Average severity and urgency
    - Distribution by priority level
    - Status breakdown

    Args:
        start_date: Start date for statistics period (optional)
        end_date: End date for statistics period (optional)

    Returns:
        Dictionary with accident statistics
    """
    try:
        db_service = SupabaseService(db)
        accident_service = AccidentHistoryService(db_service)

        stats = await accident_service.get_accident_statistics(
            start_date=start_date,
            end_date=end_date
        )

        return stats

    except Exception as e:
        logger.error(f"Error fetching accident statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_accident_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Client = Depends(get_db)
):
    """
    Get accident trends over time.

    Analyzes accident patterns over a specified time period.

    Args:
        days: Number of days to analyze (default 30, max 365)

    Returns:
        Dictionary with trend data including daily counts and trend direction
    """
    try:
        db_service = SupabaseService(db)
        accident_service = AccidentHistoryService(db_service)

        trends = await accident_service.get_accident_trends(days=days)

        return trends

    except Exception as e:
        logger.error(f"Error fetching accident trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
