"""
Reverse Geocoding Service
Converts GPS coordinates to human-readable place names using OpenStreetMap Nominatim API.
"""

import logging
from functools import lru_cache
from typing import Optional, Tuple
import httpx
import asyncio

logger = logging.getLogger(__name__)

# Nominatim API endpoint (free, no API key required)
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

# Cache timeout: 1 hour (3600 seconds)
CACHE_SIZE = 500


@lru_cache(maxsize=CACHE_SIZE)
def _cache_key(lat: float, lng: float) -> str:
    """Create cache key with rounded coordinates (to avoid cache misses from slight variations)."""
    return f"{round(lat, 4)}_{round(lng, 4)}"


# In-memory cache with rounded coordinates
_geocode_cache = {}


async def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    """
    Reverse geocode GPS coordinates to a human-readable place name.

    Args:
        lat: Latitude
        lng: Longitude

    Returns:
        str: Human-readable location name (e.g., "123 Main St, San Francisco, CA")
        None: If geocoding fails

    Example:
        >>> location = await reverse_geocode(37.7749, -122.4194)
        >>> print(location)  # "San Francisco, CA, USA"
    """
    # Check cache first (using rounded coords to increase cache hits)
    cache_key = _cache_key(lat, lng)
    if cache_key in _geocode_cache:
        logger.debug(f"Cache hit for {lat}, {lng}")
        return _geocode_cache[cache_key]

    try:
        # Make request to Nominatim API
        # User-Agent is required by Nominatim usage policy
        headers = {
            "User-Agent": "NeuraCity Smart City Platform (contact: admin@neuracity.app)"
        }

        params = {
            "lat": lat,
            "lon": lng,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18,  # Street-level detail
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers,
                timeout=5.0  # 5 second timeout
            )

            if response.status_code == 200:
                data = response.json()
                location_name = _format_location_name(data)

                # Cache the result
                _geocode_cache[cache_key] = location_name
                logger.info(f"Geocoded ({lat}, {lng}) -> {location_name}")

                return location_name
            else:
                logger.warning(f"Nominatim API returned status {response.status_code}")
                return None

    except httpx.TimeoutException:
        logger.warning(f"Timeout while geocoding ({lat}, {lng})")
        return None
    except Exception as e:
        logger.error(f"Error geocoding ({lat}, {lng}): {e}")
        return None


def _format_location_name(data: dict) -> str:
    """
    Format Nominatim response into a concise location name.

    Priority:
    1. Street address (if available)
    2. Neighborhood + City
    3. City + State
    4. Display name (fallback)
    """
    try:
        address = data.get("address", {})

        # Build location string with available components
        parts = []

        # Street address components
        house_number = address.get("house_number", "")
        road = address.get("road", "")
        if house_number and road:
            parts.append(f"{house_number} {road}")
        elif road:
            parts.append(road)

        # Neighborhood or suburb
        neighborhood = address.get("neighbourhood") or address.get("suburb")
        if neighborhood:
            parts.append(neighborhood)

        # City
        city = address.get("city") or address.get("town") or address.get("village")
        if city:
            parts.append(city)

        # State/Region
        state = address.get("state")
        if state:
            parts.append(state)

        # If we have parts, join them
        if parts:
            # Limit to first 3 parts for conciseness
            return ", ".join(parts[:3])

        # Fallback to display name
        display_name = data.get("display_name", "")
        if display_name:
            # Limit display name length
            return display_name[:80] + ("..." if len(display_name) > 80 else "")

        return "Unknown Location"

    except Exception as e:
        logger.error(f"Error formatting location name: {e}")
        return data.get("display_name", "Unknown Location")


async def batch_reverse_geocode(coordinates: list[Tuple[float, float]]) -> dict[Tuple[float, float], str]:
    """
    Reverse geocode multiple coordinates efficiently.

    Args:
        coordinates: List of (lat, lng) tuples

    Returns:
        dict: Mapping of (lat, lng) -> location_name

    Note:
        Respects Nominatim rate limit (1 request per second) for uncached requests.
    """
    results = {}

    for lat, lng in coordinates:
        location = await reverse_geocode(lat, lng)
        results[(lat, lng)] = location or f"{lat:.4f}, {lng:.4f}"

        # Rate limiting: wait 1 second between requests (Nominatim requirement)
        # Only wait if not from cache
        cache_key = _cache_key(lat, lng)
        if cache_key not in _geocode_cache:
            await asyncio.sleep(1)

    return results


def clear_cache():
    """Clear the geocoding cache (for testing or manual refresh)."""
    global _geocode_cache
    _geocode_cache = {}
    logger.info("Geocoding cache cleared")


# Synchronous version for non-async contexts
def reverse_geocode_sync(lat: float, lng: float) -> Optional[str]:
    """
    Synchronous version of reverse_geocode.
    Use only when async is not available.
    """
    try:
        import requests

        cache_key = _cache_key(lat, lng)
        if cache_key in _geocode_cache:
            return _geocode_cache[cache_key]

        headers = {
            "User-Agent": "NeuraCity Smart City Platform (contact: admin@neuracity.app)"
        }

        params = {
            "lat": lat,
            "lon": lng,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18,
        }

        response = requests.get(
            f"{NOMINATIM_BASE_URL}/reverse",
            params=params,
            headers=headers,
            timeout=5.0
        )

        if response.status_code == 200:
            data = response.json()
            location_name = _format_location_name(data)
            _geocode_cache[cache_key] = location_name
            return location_name

        return None

    except Exception as e:
        logger.error(f"Error in sync geocoding: {e}")
        return None
