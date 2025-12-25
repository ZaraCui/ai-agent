"""
Redis Cache Module for Travel Planning Agent
Provides caching utilities to improve API performance
"""
import json
import os
import hashlib
import redis
from typing import Any, Optional, Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with connection pooling and error handling"""
    
    def __init__(self):
        """Initialize Redis connection from environment variables"""
        self.enabled = os.environ.get('REDIS_ENABLED', 'False').lower() == 'true'
        
        if not self.enabled:
            logger.info("Redis cache is disabled. Set REDIS_ENABLED=True to enable.")
            self.redis_client = None
            return
        
        # Redis connection settings
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_password = os.environ.get('REDIS_PASSWORD', None)
        redis_db = int(os.environ.get('REDIS_DB', 0))
        redis_socket_timeout = int(os.environ.get('REDIS_SOCKET_TIMEOUT', 5))
        
        try:
            # Create Redis connection with connection pool
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                decode_responses=True,  # Auto-decode bytes to strings
                socket_timeout=redis_socket_timeout,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis cache connected successfully to {redis_host}:{redis_port}")
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Redis cache disabled due to connection failure")
            self.redis_client = None
            self.enabled = False
        except Exception as e:
            logger.error(f"Unexpected error initializing Redis: {e}")
            self.redis_client = None
            self.enabled = False

# Singleton instance of the cache
_cache_instance = None

def get_cache_client():
    """
    Returns a singleton instance of the RedisCache client.
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance.redis_client if _cache_instance.enabled else None

# Main cache object to be used in the application
cache = RedisCache()

def _generate_key(prefix: str, *args, **kwargs) -> str:
    """Generate a unique cache key based on function arguments"""
    # Create a stable string representation of arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())  # Sort for consistency
    }
    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"
    
def get(key: str) -> Optional[Any]:
    """Get value from cache"""
    if not cache.enabled or not cache.redis_client:
        return None
    
    try:
        value = cache.redis_client.get(key)
        if value:
            logger.debug(f"Cache hit: {key}")
            return json.loads(value)
        else:
            logger.debug(f"Cache miss: {key}")
            return None
    except Exception as e:
        logger.error(f"Error reading from cache: {e}")
        return None
    
def set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Set value in cache with TTL (time to live) in seconds
    Default TTL: 3600 seconds (1 hour)
    """
    if not cache.enabled or not cache.redis_client:
        return False
    
    try:
        serialized = json.dumps(value, ensure_ascii=False)
        cache.redis_client.setex(key, ttl, serialized)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Error writing to cache: {e}")
        return False
    
def delete(key: str) -> bool:
    """Delete a specific key from cache"""
    if not cache.enabled or not cache.redis_client:
        return False
    
    try:
        result = cache.redis_client.delete(key)
        logger.debug(f"Cache delete: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Error deleting from cache: {e}")
        return False
    
def clear_pattern(pattern: str) -> int:
    """Clear all keys matching a pattern (e.g., 'spots:*')"""
    if not cache.enabled or not cache.redis_client:
        return 0
    
    try:
        keys = cache.redis_client.keys(pattern)
        if keys:
            deleted = cache.redis_client.delete(*keys)
            logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Error clearing cache pattern: {e}")
        return 0
    
def clear_all() -> bool:
    """Clear all cache entries (use with caution!)"""
    if not cache.enabled or not cache.redis_client:
        return False
    
    try:
        cache.redis_client.flushdb()
        logger.info("All cache cleared")
        return True
    except Exception as e:
        logger.error(f"Error clearing all cache: {e}")
        return False
    
def get_stats() -> dict:
    """Get cache statistics"""
    if not cache.enabled or not cache.redis_client:
        return {
            'enabled': False,
            'message': 'Redis cache is disabled'
        }
    
    try:
        info = cache.redis_client.info()
        keys_count = cache.redis_client.dbsize()
        
        return {
            'enabled': True,
            'connected': True,
            'keys_count': keys_count,
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'uptime_in_seconds': info.get('uptime_in_seconds', 0),
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            'enabled': True,
            'connected': False,
            'error': str(e)
        }


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching function results
    
    Usage:
        @cached(prefix='my_function', ttl=7200)
        def my_function(arg1, arg2):
            # expensive operation
            return result
    
    Args:
        prefix: Cache key prefix for this function
        ttl: Time to live in seconds (default: 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # If cache is disabled, just call the function
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = _generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cache miss - call function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Helper function to invalidate cache by pattern
    
    Usage:
        invalidate_cache('spots:*')  # Clear all spots cache
        invalidate_cache('plan:*')   # Clear all planning cache
    """
    return cache.clear_pattern(pattern)


def cache_key_for_spots(city: str) -> str:
    """Generate cache key for city spots"""
    return f"spots:{city.lower()}"


def cache_key_for_cities() -> str:
    """Generate cache key for cities list"""
    return "cities:list"


def cache_key_for_plan(city: str, days: int, spots: list) -> str:
    """Generate a specific cache key for an itinerary plan."""
    spots_hash = hashlib.md5(json.dumps(sorted(spots)).encode()).hexdigest()[:8]
    return f"plan:{city}:{days}:{spots_hash}"

def cache_key_for_places(identifier: str) -> str:
    """Generate cache key for Google Places API responses."""
    # Use MD5 hash for longer identifiers to keep key length reasonable
    id_hash = hashlib.md5(identifier.encode()).hexdigest()
    return f"places:{id_hash}"
