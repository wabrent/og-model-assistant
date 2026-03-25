"""
Redis client for caching.
"""
import redis.asyncio as redis
from typing import Optional, Any
import json
from loguru import logger

from core.config import settings


class RedisCache:
    """Redis cache manager with JSON serialization support."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.default_ttl: int = 3600  # 1 hour
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.client:
            return False
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, ensure_ascii=False)
            await self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    async def get_many(self, *keys: str) -> list:
        """Get multiple values from cache."""
        if not self.client:
            return [None] * len(keys)
        try:
            values = await self.client.mget(*keys)
            return [json.loads(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Redis MGET error: {e}")
            return [None] * len(keys)


# Global cache instance
cache = RedisCache()


async def get_cache() -> RedisCache:
    """Dependency for getting cache instance."""
    return cache
