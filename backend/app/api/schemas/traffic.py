"""
Pydantic schemas for Traffic Segment entities.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TrafficSegmentResponse(BaseModel):
    """Schema for traffic segment response."""
    id: str
    segment_id: Optional[str]
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    congestion: Optional[float] = Field(None, ge=0, le=1, description="Congestion level from 0 (clear) to 1 (heavy)")
    ts: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "segment_id": "SEG_001",
                "lat": 40.7580,
                "lng": -73.9855,
                "congestion": 0.75,
                "ts": "2025-01-15T10:30:00Z"
            }
        }
