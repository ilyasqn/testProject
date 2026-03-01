import json
from typing import Any, Optional

import redis.asyncio as redis
from loguru import logger


class RedisCache:
    def __init__(self, url: str):
        self._url = url
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        self._redis = redis.from_url(self._url, decode_responses=True)
        await self._redis.ping()
        logger.info("Redis connection established")

    async def close(self):
        if self._redis is not None:
            await self._redis.close()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        if self._redis is None:
            return None
        value = await self._redis.get(key)
        if value is not None:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 60):
        if self._redis is None:
            return
        await self._redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def delete(self, key: str):
        if self._redis is None:
            return
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str):
        if self._redis is None:
            return
        async for key in self._redis.scan_iter(match=pattern):
            await self._redis.delete(key)
