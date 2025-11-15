"""
Pydantic schemas for Noise Segment entities.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NoiseSegmentResponse(BaseModel):
    """Schema for noise segment response."""
    id: str
    segment_id: Optional[str]
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    noise_db: Optional[float] = Field(None, ge=0, le=150, description="Noise level in decibels")
    ts: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "segment_id": "SEG_001",
                "lat": 40.7580,
                "lng": -73.9855,
                "noise_db": 65.5,
                "ts": "2025-01-15T10:30:00Z"
            }
        }
