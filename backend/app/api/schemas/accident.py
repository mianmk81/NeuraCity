"""
Pydantic schemas for Accident History entities.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccidentHistoryQuery(BaseModel):
    """Schema for accident history query parameters."""
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    min_lat: Optional[float] = Field(None, ge=-90, le=90, description="Minimum latitude for bounding box")
    max_lat: Optional[float] = Field(None, ge=-90, le=90, description="Maximum latitude for bounding box")
    min_lng: Optional[float] = Field(None, ge=-180, le=180, description="Minimum longitude for bounding box")
    max_lng: Optional[float] = Field(None, ge=-180, le=180, description="Maximum longitude for bounding box")


class AccidentResponse(BaseModel):
    """Schema for accident record."""
    id: str
    lat: float
    lng: float
    description: Optional[str]
    image_url: str
    severity: Optional[float]
    urgency: Optional[float]
    priority: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "lat": 40.7128,
                "lng": -74.0060,
                "description": "Vehicle collision at intersection",
                "image_url": "uploads/accident_abc123.jpg",
                "severity": 0.85,
                "urgency": 0.9,
                "priority": "critical",
                "status": "open",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class AccidentHotspot(BaseModel):
    """Schema for accident hotspot data."""
    lat: float = Field(..., description="Latitude of hotspot center (rounded to 3 decimals)")
    lng: float = Field(..., description="Longitude of hotspot center (rounded to 3 decimals)")
    accident_count: int = Field(..., description="Number of accidents in this area")
    avg_severity: Optional[float] = Field(None, description="Average severity of accidents")
    avg_urgency: Optional[float] = Field(None, description="Average urgency of accidents")
    last_accident_at: datetime = Field(..., description="Timestamp of most recent accident")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "lat": 40.713,
                "lng": -74.006,
                "accident_count": 5,
                "avg_severity": 0.75,
                "avg_urgency": 0.82,
                "last_accident_at": "2025-01-15T10:30:00Z"
            }
        }


class AccidentHistoryResponse(BaseModel):
    """Schema for paginated accident history response."""
    total: int
    page: int
    page_size: int
    accidents: list[AccidentResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 42,
                "page": 1,
                "page_size": 20,
                "accidents": []
            }
        }


class AccidentHotspotsResponse(BaseModel):
    """Schema for accident hotspots response."""
    total: int
    hotspots: list[AccidentHotspot]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 8,
                "hotspots": []
            }
        }
