"""Helper utilities for common operations."""
import math
from typing import Tuple


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance in kilometers between two GPS coordinates.
    
    Args:
        lat1, lng1: First coordinate
        lat2, lng2: Second coordinate
        
    Returns:
        float: Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_midpoint(lat1: float, lng1: float, lat2: float, lng2: float) -> Tuple[float, float]:
    """
    Calculate midpoint between two coordinates.
    
    Returns:
        Tuple of (lat, lng)
    """
    return ((lat1 + lat2) / 2, (lng1 + lng2) / 2)


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize value to 0-1 range.
    
    Args:
        value: Value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range
        
    Returns:
        float: Normalized value between 0 and 1
    """
    if max_val == min_val:
        return 0.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
