import logging

import redis.asyncio as aioredis
from redis.client import Redis

from config import settings

logger = logging.getLogger(__name__)


class TTLRedis(aioredis.Redis):

    async def set(self, key, value, *args, **kwargs):
        kwargs.setdefault("ex", settings.redis.ONE_WEEK)
        return await super().set(key, value, *args, **kwargs)


class AsyncRedisClient:
    _client: Redis = None

    @classmethod
    async def initialize(cls):

        if cls._client is None:
            cls._client = await TTLRedis.from_url(
                f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}",
                max_connections=20,
                encoding="utf8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return cls._client

    @classmethod
    async def get_client(cls):
        if cls._client is None:
            await cls.initialize()
        return cls._client


async def set_async_redis_client() -> Redis:
    client = await AsyncRedisClient.initialize()
    logger.info("AsyncRedisClient is setting...")
    return client
