"""
Pydantic schemas for Community Risk Index entities.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RiskBlockQuery(BaseModel):
    """Schema for risk block query parameters."""
    min_lat: Optional[float] = Field(None, ge=-90, le=90, description="Minimum latitude for bounding box")
    max_lat: Optional[float] = Field(None, ge=-90, le=90, description="Maximum latitude for bounding box")
    min_lng: Optional[float] = Field(None, ge=-180, le=180, description="Minimum longitude for bounding box")
    max_lng: Optional[float] = Field(None, ge=-180, le=180, description="Maximum longitude for bounding box")
    min_risk: Optional[float] = Field(None, ge=0, le=1, description="Minimum overall risk score")


class RiskComponentBreakdown(BaseModel):
    """Schema for detailed risk component breakdown."""
    accident_risk: float = Field(..., ge=0, le=1, description="Risk score from accidents (0-1)")
    infrastructure_risk: float = Field(..., ge=0, le=1, description="Risk score from infrastructure issues (0-1)")
    traffic_risk: float = Field(..., ge=0, le=1, description="Risk score from traffic congestion (0-1)")


class RiskBlockStats(BaseModel):
    """Schema for risk block statistics."""
    accident_count: int = Field(..., description="Number of accidents in block")
    pothole_count: int = Field(..., description="Number of potholes in block")
    traffic_light_count: int = Field(..., description="Number of traffic light issues in block")
    avg_congestion: float = Field(..., ge=0, le=1, description="Average traffic congestion (0-1)")
    avg_noise_db: float = Field(..., description="Average noise level in decibels")
    avg_severity: float = Field(..., ge=0, le=1, description="Average issue severity (0-1)")


class RiskBlockResponse(BaseModel):
    """Schema for risk block response."""
    block_id: str = Field(..., description="Unique block identifier")
    center_lat: float = Field(..., description="Center latitude of block")
    center_lng: float = Field(..., description="Center longitude of block")
    bounds_min_lat: float = Field(..., description="Minimum latitude of block bounds")
    bounds_min_lng: float = Field(..., description="Minimum longitude of block bounds")
    bounds_max_lat: float = Field(..., description="Maximum latitude of block bounds")
    bounds_max_lng: float = Field(..., description="Maximum longitude of block bounds")
    overall_risk: float = Field(..., ge=0, le=1, description="Composite risk score (0-1)")
    risk_breakdown: RiskComponentBreakdown
    statistics: RiskBlockStats
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "block_id": "37.750_-122.450",
                "center_lat": 37.750,
                "center_lng": -122.450,
                "bounds_min_lat": 37.745,
                "bounds_min_lng": -122.455,
                "bounds_max_lat": 37.755,
                "bounds_max_lng": -122.445,
                "overall_risk": 0.72,
                "risk_breakdown": {
                    "accident_risk": 0.85,
                    "infrastructure_risk": 0.65,
                    "traffic_risk": 0.70
                },
                "statistics": {
                    "accident_count": 5,
                    "pothole_count": 12,
                    "traffic_light_count": 2,
                    "avg_congestion": 0.68,
                    "avg_noise_db": 72.5,
                    "avg_severity": 0.63
                },
                "updated_at": "2025-01-15T10:30:00Z"
            }
        }


class RiskBlockSummary(BaseModel):
    """Schema for simplified risk block summary."""
    block_id: str
    center_lat: float
    center_lng: float
    overall_risk: float = Field(..., ge=0, le=1)
    accident_count: int
    pothole_count: int

    class Config:
        from_attributes = True


class RiskIndexResponse(BaseModel):
    """Schema for paginated risk index response."""
    total: int
    blocks: list[RiskBlockSummary]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 125,
                "blocks": []
            }
        }
