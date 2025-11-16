"""
Reverse Geocoding Service
Converts GPS coordinates to human-readable place names using OpenStreetMap Nominatim API.
"""

import logging
import json
from functools import lru_cache
from typing import Optional, Tuple
from pathlib import Path
import httpx
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Nominatim API endpoint (free, no API key required)
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

# Cache configuration
CACHE_SIZE = 500
CACHE_FILE = Path("backend/data/geocode_cache.json")  # Persistent cache file
CACHE_DIR = CACHE_FILE.parent

# Rate limiting: Nominatim allows 1 request per second
# Use a semaphore to limit concurrent requests
_geocode_semaphore = asyncio.Semaphore(1)  # Only 1 concurrent request
_last_request_time = None
_min_request_interval = timedelta(seconds=1.1)  # 1.1 seconds between requests

# Track if cache has been modified (for periodic saves)
_cache_modified = False


@lru_cache(maxsize=CACHE_SIZE)
def _cache_key(lat: float, lng: float) -> str:
    """Create cache key with rounded coordinates (to avoid cache misses from slight variations)."""
    return f"{round(lat, 4)}_{round(lng, 4)}"


def _load_cache_from_file() -> dict:
    """Load geocoding cache from JSON file."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                logger.info(f"Loaded {len(cache_data)} geocoding entries from cache file")
                return cache_data
        else:
            logger.info("No geocoding cache file found, starting fresh")
            return {}
    except Exception as e:
        logger.warning(f"Failed to load geocoding cache: {e}")
        return {}


def _save_cache_to_file():
    """Save geocoding cache to JSON file."""
    global _cache_modified
    try:
        # Create cache directory if it doesn't exist
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save to temporary file first, then rename (atomic write)
        temp_file = CACHE_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(_geocode_cache, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        temp_file.replace(CACHE_FILE)
        _cache_modified = False
        logger.debug(f"Saved {len(_geocode_cache)} geocoding entries to cache file")
    except Exception as e:
        logger.error(f"Failed to save geocoding cache: {e}")


# In-memory cache with rounded coordinates (loaded from file on startup)
_geocode_cache = _load_cache_from_file()


async def reverse_geocode(lat: float, lng: float, retries: int = 2) -> Optional[str]:
    """
    Reverse geocode GPS coordinates to a human-readable place name.

    Args:
        lat: Latitude
        lng: Longitude
        retries: Number of retry attempts (default: 2)

    Returns:
        str: Human-readable location name (e.g., "123 Main St, San Francisco, CA")
        None: If geocoding fails

    Example:
        >>> location = await reverse_geocode(37.7749, -122.4194)
        >>> print(location)  # "San Francisco, CA, USA"
    """
    global _cache_modified
    
    # Check cache first (using rounded coords to increase cache hits)
    cache_key = _cache_key(lat, lng)
    if cache_key in _geocode_cache:
        logger.debug(f"Cache hit for {lat}, {lng}")
        return _geocode_cache[cache_key]

    # Use semaphore to limit concurrent requests and respect rate limits
    async with _geocode_semaphore:
        global _last_request_time
        
        # Rate limiting: wait if needed
        if _last_request_time:
            time_since_last = datetime.now() - _last_request_time
            if time_since_last < _min_request_interval:
                wait_time = (_min_request_interval - time_since_last).total_seconds()
                await asyncio.sleep(wait_time)
        
        _last_request_time = datetime.now()

        # Retry logic with exponential backoff
        for attempt in range(retries + 1):
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

                # Increase timeout to 10 seconds for better reliability
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{NOMINATIM_BASE_URL}/reverse",
                        params=params,
                        headers=headers,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        location_name = _format_location_name(data)

                        # Cache the result (both in-memory and mark for file save)
                        _geocode_cache[cache_key] = location_name
                        _cache_modified = True
                        logger.info(f"Geocoded ({lat}, {lng}) -> {location_name}")

                        # Save cache periodically (every 10 new entries to avoid too frequent writes)
                        if len(_geocode_cache) % 10 == 0:
                            _save_cache_to_file()

                        return location_name
                    elif response.status_code == 429:  # Rate limited
                        wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"Nominatim API returned status {response.status_code}")
                        return None

            except httpx.TimeoutException:
                if attempt < retries:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    logger.debug(f"Timeout while geocoding ({lat}, {lng}), retrying in {wait_time}s (attempt {attempt + 1}/{retries})")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"Timeout while geocoding ({lat}, {lng}) after {retries + 1} attempts")
                    return None
            except Exception as e:
                if attempt < retries:
                    wait_time = (2 ** attempt) * 1
                    logger.debug(f"Error geocoding ({lat}, {lng}): {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error geocoding ({lat}, {lng}) after {retries + 1} attempts: {e}")
                    return None

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
    Checks file cache first, only makes API calls for uncached coordinates.

    Args:
        coordinates: List of (lat, lng) tuples

    Returns:
        dict: Mapping of (lat, lng) -> location_name

    Note:
        Respects Nominatim rate limit (1 request per second) for uncached requests.
        File cache is checked first for instant lookups.
    """
    results = {}
    uncached_coords = []

    # First pass: Check cache for all coordinates (fast, no API calls)
    for lat, lng in coordinates:
        cache_key = _cache_key(lat, lng)
        if cache_key in _geocode_cache:
            # Cache hit - instant lookup
            results[(lat, lng)] = _geocode_cache[cache_key]
        else:
            # Cache miss - will need to geocode
            uncached_coords.append((lat, lng))

    # Second pass: Only geocode uncached coordinates (respects rate limits)
    # This minimizes API calls and wait time
    for lat, lng in uncached_coords:
        location = await reverse_geocode(lat, lng)
        results[(lat, lng)] = location or f"{lat:.4f}, {lng:.4f}"

    return results


def clear_cache():
    """Clear the geocoding cache (both in-memory and file)."""
    global _geocode_cache, _cache_modified
    _geocode_cache = {}
    _cache_modified = True
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    logger.info("Geocoding cache cleared")


def save_cache():
    """Manually save cache to file (useful for shutdown hooks)."""
    if _cache_modified:
        _save_cache_to_file()


# Synchronous version for non-async contexts
def reverse_geocode_sync(lat: float, lng: float) -> Optional[str]:
    """
    Synchronous version of reverse_geocode.
    Use only when async is not available.
    """
    global _cache_modified
    
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
            _cache_modified = True
            # Save cache periodically
            if len(_geocode_cache) % 10 == 0:
                _save_cache_to_file()
            return location_name

        return None

    except Exception as e:
        logger.error(f"Error in sync geocoding: {e}")
        return None
