"""Validation utilities for input data."""
from fastapi import HTTPException
import re


def validate_gps_coordinates(lat: float, lng: float):
    """Validate GPS coordinates are within valid ranges."""
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid latitude: {lat}. Must be between -90 and 90."
        )
    if not (-180 <= lng <= 180):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid longitude: {lng}. Must be between -180 and 180."
        )
    return True


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))
