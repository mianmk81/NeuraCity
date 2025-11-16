"""API endpoints for Community Risk Index."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from supabase import Client

from app.api.schemas.risk import RiskIndexResponse, RiskBlockResponse
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
from app.services.risk_index_service import RiskIndexService
from app.utils.cache import cached_response, RISK_INDEX_CACHE
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risk-index", tags=["risk-index"])


@router.get("", response_model=RiskIndexResponse)
async def get_risk_index(
    min_lat: float = Query(..., ge=-90, le=90, description="Minimum latitude for bounding box"),
    max_lat: float = Query(..., ge=-90, le=90, description="Maximum latitude for bounding box"),
    min_lng: float = Query(..., ge=-180, le=180, description="Minimum longitude for bounding box"),
    max_lng: float = Query(..., ge=-180, le=180, description="Maximum longitude for bounding box"),
    min_risk: Optional[float] = Query(None, ge=0, le=1, description="Minimum overall risk score filter"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of blocks to return"),
    db: Client = Depends(get_db)
):
    """
    Get risk scores for blocks within a bounding box.

    Returns precomputed risk scores for geographic blocks. Each block contains
    composite risk scores derived from multiple factors:
    - Accident frequency and severity
    - Infrastructure issues (potholes, traffic lights)
    - Traffic congestion levels

    Args:
        min_lat: Minimum latitude of bounding box (required)
        max_lat: Maximum latitude of bounding box (required)
        min_lng: Minimum longitude of bounding box (required)
        max_lng: Maximum longitude of bounding box (required)
        min_risk: Filter blocks with risk >= this value (optional, 0-1)
        limit: Maximum number of blocks to return (default 100, max 500)

    Returns:
        List of risk blocks with scores and statistics
    """
    async def _get_risk_blocks():
        db_service = SupabaseService(db)
        risk_service = RiskIndexService(db_service)

        result = await risk_service.get_risk_blocks_in_bounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            min_risk=min_risk,
            limit=limit
        )

        return result

    try:
        # Use caching for risk index queries
        @cached_response(RISK_INDEX_CACHE, "risk_index")
        async def cached_risk_index(minlat, maxlat, minlng, maxlng, minrisk, lim):
            return await _get_risk_blocks()

        result = await cached_risk_index(min_lat, max_lat, min_lng, max_lng, min_risk, limit)

        return result

    except Exception as e:
        logger.error(f"Error fetching risk index: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{block_id}", response_model=RiskBlockResponse)
async def get_risk_block_details(
    block_id: str,
    db: Client = Depends(get_db)
):
    """
    Get detailed risk breakdown for a specific block.

    Provides comprehensive risk information including:
    - Overall composite risk score
    - Component risk scores (accident, infrastructure, traffic)
    - Detailed statistics (counts, averages)
    - Geographic bounds

    Args:
        block_id: Block identifier (format: "lat_lng", e.g., "37.75_-122.45")

    Returns:
        Detailed risk block data with full breakdown
    """
    async def _get_block_details():
        db_service = SupabaseService(db)
        risk_service = RiskIndexService(db_service)

        block = await risk_service.get_risk_block_details(block_id)

        if not block:
            raise HTTPException(status_code=404, detail="Risk block not found")

        return block

    try:
        # Cache individual block details
        @cached_response(RISK_INDEX_CACHE, "risk_block_details")
        async def cached_block_details(bid):
            return await _get_block_details()

        result = await cached_block_details(block_id)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk block details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate")
async def calculate_risk_for_area(
    min_lat: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    max_lat: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    min_lng: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    max_lng: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    block_size: float = Query(0.01, ge=0.001, le=0.1, description="Block size in degrees (~1km = 0.01)"),
    db: Client = Depends(get_db)
):
    """
    Recalculate risk scores for all blocks in an area.

    This endpoint triggers a recalculation of risk scores for all blocks
    within the specified bounding box. Use this after new issues are reported
    or to refresh stale data.

    WARNING: This can be computationally expensive for large areas.
    Consider limiting the bounding box size.

    Args:
        min_lat: Minimum latitude of area
        max_lat: Maximum latitude of area
        min_lng: Minimum longitude of area
        max_lng: Maximum longitude of area
        block_size: Size of each block in degrees (default 0.01 ~ 1km)

    Returns:
        Number of blocks updated
    """
    try:
        # Validate bounding box size to prevent abuse
        lat_diff = max_lat - min_lat
        lng_diff = max_lng - min_lng

        if lat_diff > 0.5 or lng_diff > 0.5:
            raise HTTPException(
                status_code=400,
                detail="Bounding box too large. Maximum size is 0.5 degrees (~55km)"
            )

        db_service = SupabaseService(db)
        risk_service = RiskIndexService(db_service)

        blocks_updated = await risk_service.update_risk_blocks_in_area(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            block_size=block_size
        )

        logger.info(f"Calculated risk for {blocks_updated} blocks")

        return {
            "blocks_updated": blocks_updated,
            "message": f"Successfully recalculated risk for {blocks_updated} blocks"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating risk blocks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/high-risk-areas")
async def get_high_risk_areas(
    min_risk: float = Query(0.6, ge=0, le=1, description="Minimum risk threshold"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of areas to return"),
    db: Client = Depends(get_db)
):
    """
    Get all high-risk areas above a threshold.

    Identifies geographic areas with elevated risk scores for
    focused attention and resource allocation.

    Args:
        min_risk: Minimum risk score threshold (default 0.6, range 0-1)
        limit: Maximum number of areas to return (default 50, max 200)

    Returns:
        List of high-risk blocks sorted by risk score descending
    """
    try:
        db_service = SupabaseService(db)

        # Query high-risk areas directly from database
        blocks = await db_service.get_risk_blocks(
            min_risk=min_risk,
            limit=limit
        )

        return {
            "total": len(blocks),
            "min_risk_threshold": min_risk,
            "high_risk_areas": blocks
        }

    except Exception as e:
        logger.error(f"Error fetching high-risk areas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
