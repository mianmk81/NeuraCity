"""
Pydantic schemas for User and Gamification entities.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    avatar_url: Optional[str] = Field(None, description="URL to user avatar")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Username validation."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "username": "citizen_123",
                "email": "user@example.com",
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Doe",
                "avatar_url": "https://example.com/new_avatar.jpg"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response with gamification data."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    total_points: int
    rank: int
    issues_reported: int
    issues_verified: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "citizen_123",
                "email": "user@example.com",
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "total_points": 450,
                "rank": 12,
                "issues_reported": 15,
                "issues_verified": 8,
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class PointsHistoryResponse(BaseModel):
    """Schema for points history entry."""
    id: str
    user_id: str
    points: int
    action_type: str
    issue_id: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "points": 50,
                "action_type": "issue_reported",
                "issue_id": "123e4567-e89b-12d3-a456-426614174002",
                "description": "Reported pothole on Main St",
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""
    id: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    total_points: int
    rank: int
    issues_reported: int
    issues_verified: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "top_citizen",
                "full_name": "Alice Smith",
                "avatar_url": "https://example.com/avatar.jpg",
                "total_points": 1250,
                "rank": 1,
                "issues_reported": 42,
                "issues_verified": 28
            }
        }


class LeaderboardResponse(BaseModel):
    """Schema for paginated leaderboard response."""
    total: int
    page: int
    page_size: int
    entries: list[LeaderboardEntry]

    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "page_size": 10,
                "entries": []
            }
        }
