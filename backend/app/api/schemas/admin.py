"""
Pydantic schemas for Admin entities (emergency queue and work orders).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class EmergencyStatus(str, Enum):
    """Valid emergency statuses."""
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"


class WorkOrderStatus(str, Enum):
    """Valid work order statuses."""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class EmergencyResponse(BaseModel):
    """Schema for emergency queue response."""
    id: str
    issue_id: str
    summary: Optional[str] = Field(None, description="AI-generated emergency summary")
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "issue_id": "456e7890-e89b-12d3-a456-426614174000",
                "summary": "Multi-vehicle accident on Highway 101. Emergency services required.",
                "status": "pending",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class EmergencyUpdate(BaseModel):
    """Schema for updating emergency status."""
    status: EmergencyStatus

    class Config:
        json_schema_extra = {
            "example": {
                "status": "dispatched"
            }
        }


class WorkOrderResponse(BaseModel):
    """Schema for work order response."""
    id: str
    issue_id: str
    contractor_id: Optional[str]
    contractor_name: Optional[str] = None
    contractor_specialty: Optional[str] = None
    material_suggestion: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "issue_id": "456e7890-e89b-12d3-a456-426614174000",
                "contractor_id": "789e0123-e89b-12d3-a456-426614174000",
                "contractor_name": "City Road Repair Inc.",
                "contractor_specialty": "pothole_repair",
                "material_suggestion": "Asphalt mix, gravel, sealant",
                "status": "pending_review",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class WorkOrderUpdate(BaseModel):
    """Schema for updating work order."""
    status: Optional[WorkOrderStatus] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved"
            }
        }


class ContractorResponse(BaseModel):
    """Schema for contractor response."""
    id: str
    name: Optional[str]
    specialty: Optional[str]
    contact_email: Optional[str]
    has_city_contract: Optional[bool]

    class Config:
        from_attributes = True
