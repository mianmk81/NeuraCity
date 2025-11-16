"""
Response Caching Utility
Provides TTL-based caching for API responses to improve performance.
"""
from cachetools import TTLCache
from functools import wraps
import hashlib
import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Configure caches with different TTLs for different data types
LEADERBOARD_CACHE = TTLCache(maxsize=100, ttl=60)  # 1 minute
ACCIDENT_HISTORY_CACHE = TTLCache(maxsize=500, ttl=300)  # 5 minutes
RISK_INDEX_CACHE = TTLCache(maxsize=1000, ttl=600)  # 10 minutes
GENERAL_CACHE = TTLCache(maxsize=200, ttl=120)  # 2 minutes


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        prefix: Key prefix (usually function name)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of serialized arguments
    """
    key_dict = {
        "args": str(args),
        "kwargs": {k: str(v) for k, v in sorted(kwargs.items())}
    }
    key_str = f"{prefix}:{json.dumps(key_dict, sort_keys=True)}"
    return hashlib.md5(key_str.encode()).hexdigest()


def cached_response(cache: TTLCache, key_prefix: str = None):
    """
    Decorator for caching API responses.

    Args:
        cache: TTLCache instance to use
        key_prefix: Optional prefix for cache keys

    Usage:
        @cached_response(LEADERBOARD_CACHE, "leaderboard")
        async def get_leaderboard(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Check cache
            if cache_key in cache:
                logger.debug(f"Cache HIT for {prefix} (key: {cache_key[:8]}...)")
                return cache[cache_key]

            # Cache miss - call function
            logger.debug(f"Cache MISS for {prefix} (key: {cache_key[:8]}...)")
            result = await func(*args, **kwargs)

            # Store in cache
            cache[cache_key] = result

            return result

        return wrapper
    return decorator


def invalidate_cache(cache: TTLCache, pattern: str = None):
    """
    Invalidate cache entries.

    Args:
        cache: TTLCache instance
        pattern: Optional pattern to match keys (None = clear all)
    """
    if pattern is None:
        cache.clear()
        logger.info(f"Cleared entire cache (size before: {len(cache)})")
    else:
        # TTLCache doesn't support pattern matching, so we clear all
        # In production, consider using Redis for more advanced cache invalidation
        cache.clear()
        logger.info(f"Cleared cache with pattern: {pattern}")


def get_cache_stats(cache: TTLCache) -> dict:
    """
    Get statistics about a cache.

    Args:
        cache: TTLCache instance

    Returns:
        Dictionary with cache statistics
    """
    return {
        "size": len(cache),
        "maxsize": cache.maxsize,
        "ttl": cache.ttl,
        "utilization": len(cache) / cache.maxsize if cache.maxsize > 0 else 0
    }
