"""
Pydantic schemas for Routing entities.
"""
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from enum import Enum


class RouteType(str, Enum):
    """Valid route types."""
    DRIVE = "drive"
    ECO = "eco"
    QUIET_WALK = "quiet_walk"


class RoutePlanRequest(BaseModel):
    """Schema for route planning request."""
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    route_type: RouteType

    class Config:
        json_schema_extra = {
            "example": {
                "origin_lat": 40.7128,
                "origin_lng": -74.0060,
                "destination_lat": 40.7580,
                "destination_lng": -73.9855,
                "route_type": "drive"
            }
        }


class RouteMetrics(BaseModel):
    """Metrics for a calculated route."""
    distance_km: float = Field(..., description="Total distance in kilometers")
    eta_minutes: float = Field(..., description="Estimated time of arrival in minutes")
    co2_kg: Optional[float] = Field(None, description="Estimated CO2 emissions in kg (for drive/eco)")
    avg_noise_db: Optional[float] = Field(None, description="Average noise level in dB (for quiet_walk)")
    congestion_score: Optional[float] = Field(None, description="Average congestion (0-1)")


class RouteResponse(BaseModel):
    """Schema for route response."""
    route_type: str
    path: List[Tuple[float, float]] = Field(..., description="List of (lat, lng) coordinates")
    metrics: RouteMetrics
    explanation: Optional[str] = Field(None, description="AI-generated route explanation")

    class Config:
        json_schema_extra = {
            "example": {
                "route_type": "drive",
                "path": [[40.7128, -74.0060], [40.7580, -73.9855]],
                "metrics": {
                    "distance_km": 8.5,
                    "eta_minutes": 22,
                    "co2_kg": 1.2,
                    "congestion_score": 0.3
                },
                "explanation": "This route avoids high-traffic areas and reported accidents."
            }
        }
