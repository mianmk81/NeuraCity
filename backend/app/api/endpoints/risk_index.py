"""Risk Index API endpoints."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from app.api.schemas.risk_index import (
    RiskBlockResponse,
    RiskBlockCreate,
    RiskBlockUpdate,
    RiskFactorResponse,
    RiskHistoryResponse,
    RiskConfigResponse,
    RecalculateRiskRequest,
    RecalculateRiskResponse
)
from app.services.supabase_service import SupabaseService
from app.core.dependencies import get_supabase_service
from app.services import risk_index_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk-index", tags=["Risk Index"])


# =====================================================
# RISK BLOCKS ENDPOINTS
# =====================================================

@router.get("/blocks", response_model=List[RiskBlockResponse])
async def get_risk_blocks(
    risk_category: Optional[str] = Query(None, description="Filter by risk category (low, moderate, high, critical)"),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum composite risk index"),
    max_risk: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum composite risk index"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of results"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """
    Get risk blocks with optional filtering.

    Filters:
    - risk_category: low, moderate, high, critical
    - min_risk/max_risk: composite_risk_index range (0-1)
    - limit: max results to return
    """
    try:
        blocks = await db.get_risk_blocks(
            risk_category=risk_category,
            min_risk=min_risk,
            max_risk=max_risk,
            limit=limit
        )
        return blocks
    except Exception as e:
        logger.error(f"Error fetching risk blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk blocks: {str(e)}")


@router.get("/blocks/{block_id}", response_model=RiskBlockResponse)
async def get_risk_block(
    block_id: str,
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get a specific risk block by block_id."""
    try:
        block = await db.get_risk_block_by_id(block_id)
        if not block:
            raise HTTPException(status_code=404, detail=f"Risk block {block_id} not found")
        return block
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk block {block_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk block: {str(e)}")


@router.get("/blocks/bounds", response_model=List[RiskBlockResponse])
async def get_risk_blocks_in_bounds(
    lat_min: float = Query(..., ge=-90, le=90, description="Minimum latitude"),
    lat_max: float = Query(..., ge=-90, le=90, description="Maximum latitude"),
    lng_min: float = Query(..., ge=-180, le=180, description="Minimum longitude"),
    lng_max: float = Query(..., ge=-180, le=180, description="Maximum longitude"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get risk blocks within geographic bounds (bounding box)."""
    try:
        blocks = await db.get_risk_blocks_in_bounds(lat_min, lat_max, lng_min, lng_max)
        return blocks
    except Exception as e:
        logger.error(f"Error fetching risk blocks in bounds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk blocks: {str(e)}")


@router.put("/blocks/{block_id}", response_model=RiskBlockResponse)
async def update_risk_block(
    block_id: str,
    update_data: RiskBlockUpdate,
    db: SupabaseService = Depends(get_supabase_service)
):
    """Update a risk block's scores."""
    try:
        # Verify block exists
        existing = await db.get_risk_block_by_id(block_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Risk block {block_id} not found")

        # Update block
        update_dict = update_data.dict(exclude_unset=True)
        update_dict['last_calculated_at'] = datetime.now().isoformat()

        updated_block = await db.update_risk_block(block_id, update_dict)
        return updated_block
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating risk block {block_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update risk block: {str(e)}")


# =====================================================
# RISK FACTORS ENDPOINTS
# =====================================================

@router.get("/factors", response_model=List[RiskFactorResponse])
async def get_risk_factors(
    block_id: Optional[str] = Query(None, description="Filter by block_id"),
    factor_type: Optional[str] = Query(None, description="Filter by factor type"),
    limit: int = Query(1000, ge=1, le=5000, description="Maximum number of results"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """
    Get risk factor measurements.

    Filters:
    - block_id: specific block
    - factor_type: crime, blight, emergency_response, air_quality, heat_exposure, traffic_speed
    """
    try:
        factors = await db.get_risk_factors(
            block_id=block_id,
            factor_type=factor_type,
            limit=limit
        )
        return factors
    except Exception as e:
        logger.error(f"Error fetching risk factors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk factors: {str(e)}")


# =====================================================
# RISK HISTORY ENDPOINTS
# =====================================================

@router.get("/history/{block_id}", response_model=List[RiskHistoryResponse])
async def get_risk_history(
    block_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get historical risk data for a block."""
    try:
        history = await db.get_risk_history(block_id, days)
        return history
    except Exception as e:
        logger.error(f"Error fetching risk history for {block_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk history: {str(e)}")


# =====================================================
# RISK CONFIG ENDPOINTS
# =====================================================

@router.get("/config/{config_name}", response_model=RiskConfigResponse)
async def get_risk_config(
    config_name: str = "default",
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get risk calculation configuration."""
    try:
        config = await db.get_risk_config(config_name)
        if not config:
            raise HTTPException(status_code=404, detail=f"Config {config_name} not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk config {config_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk config: {str(e)}")


# =====================================================
# RECALCULATION ENDPOINTS
# =====================================================

@router.post("/recalculate", response_model=RecalculateRiskResponse)
async def recalculate_risk_for_block(
    request: RecalculateRiskRequest,
    db: SupabaseService = Depends(get_supabase_service)
):
    """
    Recalculate risk scores for a specific block.

    Provide raw data for each risk factor and receive calculated scores.
    """
    try:
        # Load configuration
        config_data = await db.get_risk_config(request.config_name or "default")
        if config_data:
            config = risk_index_service.RiskConfig(
                crime_weight=config_data.get('crime_weight', 0.25),
                blight_weight=config_data.get('blight_weight', 0.15),
                emergency_response_weight=config_data.get('emergency_response_weight', 0.20),
                air_quality_weight=config_data.get('air_quality_weight', 0.15),
                heat_exposure_weight=config_data.get('heat_exposure_weight', 0.10),
                traffic_speed_weight=config_data.get('traffic_speed_weight', 0.15),
                crime_max_incidents=config_data.get('crime_max_incidents', 50),
                blight_max_properties=config_data.get('blight_max_properties', 20),
                emergency_max_minutes=config_data.get('emergency_max_minutes', 30),
                air_quality_max_aqi=config_data.get('air_quality_max_aqi', 200),
                heat_exposure_max_celsius=config_data.get('heat_exposure_max_celsius', 45.0),
                traffic_speed_max_mph=config_data.get('traffic_speed_max_mph', 65),
                spatial_radius_meters=config_data.get('spatial_radius_meters', 500.0),
                spatial_decay_factor=config_data.get('spatial_decay_factor', 0.5)
            )
        else:
            config = risk_index_service.DEFAULT_CONFIG

        # Calculate risk scores
        result = risk_index_service.calculate_risk_for_block(
            block_id=request.block_id,
            lat=request.lat,
            lng=request.lng,
            crime_data=request.crime_data.dict() if request.crime_data else {},
            blight_data=request.blight_data.dict() if request.blight_data else {},
            emergency_data=request.emergency_data.dict() if request.emergency_data else {},
            air_quality_data=request.air_quality_data.dict() if request.air_quality_data else {},
            heat_data=request.heat_data.dict() if request.heat_data else {},
            traffic_data=request.traffic_data.dict() if request.traffic_data else {},
            config=config
        )

        # Apply spatial smoothing if requested
        if request.apply_spatial_smoothing:
            # Get nearby blocks
            radius_deg = config.spatial_radius_meters / 111000  # Approximate degrees
            nearby_blocks = await db.get_risk_blocks_in_bounds(
                request.lat - radius_deg,
                request.lat + radius_deg,
                request.lng - radius_deg,
                request.lng + radius_deg
            )

            # Filter out the target block
            nearby_blocks = [b for b in nearby_blocks if b['block_id'] != request.block_id]

            if nearby_blocks:
                smoothed_risk = risk_index_service.apply_spatial_smoothing(
                    request.lat,
                    request.lng,
                    result['composite_risk_index'],
                    nearby_blocks,
                    config
                )
                result['composite_risk_index'] = smoothed_risk

                # Recalculate category after smoothing
                if smoothed_risk < 0.3:
                    result['risk_category'] = 'low'
                elif smoothed_risk < 0.5:
                    result['risk_category'] = 'moderate'
                elif smoothed_risk < 0.7:
                    result['risk_category'] = 'high'
                else:
                    result['risk_category'] = 'critical'

        # Update database if requested
        if request.save_to_database:
            existing = await db.get_risk_block_by_id(request.block_id)
            if existing:
                await db.update_risk_block(request.block_id, result)
            else:
                await db.create_risk_block(result)

        return result
    except Exception as e:
        logger.error(f"Error recalculating risk for {request.block_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to recalculate risk: {str(e)}")


@router.post("/recalculate-all")
async def recalculate_all_risk_blocks(
    config_name: str = Query("default", description="Configuration to use"),
    apply_spatial_smoothing: bool = Query(True, description="Apply spatial smoothing"),
    db: SupabaseService = Depends(get_supabase_service)
):
    """
    Recalculate risk scores for all blocks.

    WARNING: This is a heavy operation. Use sparingly.
    Typically used after updating configuration or bulk data import.
    """
    try:
        # Get all blocks
        blocks = await db.get_risk_blocks(limit=10000)

        if not blocks:
            return {
                "message": "No blocks to recalculate",
                "blocks_updated": 0
            }

        # Load configuration
        config_data = await db.get_risk_config(config_name)
        if config_data:
            config = risk_index_service.RiskConfig(
                crime_weight=config_data.get('crime_weight', 0.25),
                blight_weight=config_data.get('blight_weight', 0.15),
                emergency_response_weight=config_data.get('emergency_response_weight', 0.20),
                air_quality_weight=config_data.get('air_quality_weight', 0.15),
                heat_exposure_weight=config_data.get('heat_exposure_weight', 0.10),
                traffic_speed_weight=config_data.get('traffic_speed_weight', 0.15)
            )
        else:
            config = risk_index_service.DEFAULT_CONFIG

        updated_blocks = []
        for block in blocks:
            # Recalculate composite score
            composite_result = risk_index_service.calculate_composite_risk_index(
                block['crime_score'],
                block['blight_score'],
                block['emergency_response_score'],
                block['air_quality_score'],
                block['heat_exposure_score'],
                block['traffic_speed_score'],
                config
            )

            block['composite_risk_index'] = composite_result['composite_risk_index']
            block['risk_category'] = composite_result['risk_category']
            block['last_calculated_at'] = datetime.now().isoformat()

            updated_blocks.append(block)

        # Batch update
        await db.batch_upsert_risk_blocks(updated_blocks)

        return {
            "message": f"Successfully recalculated {len(updated_blocks)} blocks",
            "blocks_updated": len(updated_blocks),
            "config_used": config_name
        }
    except Exception as e:
        logger.error(f"Error recalculating all risk blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to recalculate: {str(e)}")


# =====================================================
# STATISTICS ENDPOINTS
# =====================================================

@router.get("/statistics")
async def get_risk_statistics(
    db: SupabaseService = Depends(get_supabase_service)
):
    """Get overall risk statistics across all blocks."""
    try:
        blocks = await db.get_risk_blocks(limit=10000)

        if not blocks:
            return {
                "total_blocks": 0,
                "message": "No risk data available"
            }

        # Calculate statistics
        total_blocks = len(blocks)
        categories = {'low': 0, 'moderate': 0, 'high': 0, 'critical': 0}
        total_risk = 0
        max_risk_block = None
        max_risk = 0

        for block in blocks:
            categories[block['risk_category']] += 1
            total_risk += block['composite_risk_index']

            if block['composite_risk_index'] > max_risk:
                max_risk = block['composite_risk_index']
                max_risk_block = block['block_id']

        avg_risk = total_risk / total_blocks if total_blocks > 0 else 0

        return {
            "total_blocks": total_blocks,
            "average_risk_index": round(avg_risk, 3),
            "max_risk_index": round(max_risk, 3),
            "max_risk_block_id": max_risk_block,
            "category_distribution": {
                "low": {
                    "count": categories['low'],
                    "percentage": round((categories['low'] / total_blocks) * 100, 1)
                },
                "moderate": {
                    "count": categories['moderate'],
                    "percentage": round((categories['moderate'] / total_blocks) * 100, 1)
                },
                "high": {
                    "count": categories['high'],
                    "percentage": round((categories['high'] / total_blocks) * 100, 1)
                },
                "critical": {
                    "count": categories['critical'],
                    "percentage": round((categories['critical'] / total_blocks) * 100, 1)
                }
            }
        }
    except Exception as e:
        logger.error(f"Error calculating risk statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate statistics: {str(e)}")
