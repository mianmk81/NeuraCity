"""API endpoints for route planning."""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from datetime import datetime

from app.api.schemas.routing import RoutePlanRequest, RouteResponse
from app.core.dependencies import get_db
from app.services.supabase_service import SupabaseService
from app.services.ml_routing_service import plan_route_ml
from app.utils.validators import validate_gps_coordinates
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/plan", tags=["routing"])


@router.post("", response_model=RouteResponse)
async def plan_route_endpoint(
    request: RoutePlanRequest,
    db: Client = Depends(get_db)
):
    """
    Plan a route between origin and destination.
    
    Route types:
    - drive: Avoids high-severity issues and accidents
    - eco: Minimizes CO2 emissions and congestion
    - quiet_walk: Prefers low-noise segments
    """
    try:
        validate_gps_coordinates(request.origin_lat, request.origin_lng)
        validate_gps_coordinates(request.destination_lat, request.destination_lng)
        
        db_service = SupabaseService(db)
        
        issues = await db_service.get_issues(limit=500)
        traffic = await db_service.get_traffic_segments()
        noise = await db_service.get_noise_segments()
        
        # Use ML-based routing with context
        route = await plan_route_ml(
            origin_lat=request.origin_lat,
            origin_lng=request.origin_lng,
            dest_lat=request.destination_lat,
            dest_lng=request.destination_lng,
            route_type=request.route_type,
            issues=issues,
            traffic=traffic,
            noise=noise,
            time_of_day=datetime.utcnow(),
            weather=None  # Could add weather API later
        )
        
        logger.info(f"Planned {request.route_type} route: {route['metrics']['distance_km']}km")
        return route
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error planning route: {e}")
        raise HTTPException(status_code=500, detail=str(e))
