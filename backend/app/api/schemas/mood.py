"""
Pydantic schemas for Mood Area entities.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MoodAreaResponse(BaseModel):
    """Schema for mood area response."""
    id: str
    area_id: Optional[str]
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    mood_score: Optional[float] = Field(None, ge=-1, le=1, description="Mood score from -1 (negative) to +1 (positive)")
    post_count: Optional[int] = Field(None, ge=0)
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "area_id": "MIDTOWN",
                "lat": 40.7580,
                "lng": -73.9855,
                "mood_score": 0.65,
                "post_count": 120,
                "created_at": "2025-01-15T10:30:00Z"
            }
        }
