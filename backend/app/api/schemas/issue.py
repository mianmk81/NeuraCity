"""
Pydantic schemas for Issue entities.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class IssueType(str, Enum):
    """Valid issue types."""
    ACCIDENT = "accident"
    POTHOLE = "pothole"
    TRAFFIC_LIGHT = "traffic_light"
    OTHER = "other"


class IssueStatus(str, Enum):
    """Valid issue statuses."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Priority(str, Enum):
    """Valid priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    """Valid action types."""
    EMERGENCY = "emergency"
    WORK_ORDER = "work_order"
    MONITOR = "monitor"


class IssueCreate(BaseModel):
    """Schema for creating a new issue."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    lng: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    issue_type: IssueType = Field(..., description="Type of issue")
    description: Optional[str] = Field(None, max_length=500, description="Issue description")

    @field_validator('description')
    @classmethod
    def validate_description(cls, v, info):
        """Require description if issue_type is 'other'."""
        if info.data.get('issue_type') == IssueType.OTHER and (not v or not v.strip()):
            raise ValueError("Description is required when issue_type is 'other'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "lat": 40.7128,
                "lng": -74.0060,
                "issue_type": "pothole",
                "description": "Large pothole on Main Street"
            }
        }


class IssueUpdate(BaseModel):
    """Schema for updating an existing issue."""
    status: Optional[IssueStatus] = None
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "in_progress",
                "description": "Work crew dispatched"
            }
        }


class IssueResponse(BaseModel):
    """Schema for issue response."""
    id: str
    lat: float
    lng: float
    issue_type: str
    description: Optional[str]
    image_url: str
    severity: Optional[float] = Field(None, ge=0, le=1)
    urgency: Optional[float] = Field(None, ge=0, le=1)
    priority: Optional[str]
    action_type: Optional[str]
    status: str
    location_name: Optional[str] = Field(None, description="Human-readable location name from reverse geocoding")
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "lat": 40.7128,
                "lng": -74.0060,
                "issue_type": "pothole",
                "description": "Large pothole on Main Street",
                "image_url": "uploads/issue_abc123.jpg",
                "severity": 0.7,
                "urgency": 0.8,
                "priority": "high",
                "action_type": "work_order",
                "status": "open",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }
