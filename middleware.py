from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from config import settings
from redis_client.redis import AsyncRedisClient


class RateLimitMiddleware(BaseMiddleware):
    def __init__(
        self,
        limit: int = settings.redis.limit,
        period: int = settings.redis.period,
    ):
        self.limit = limit
        self.period = period
        super().__init__()

    async def __call__(self, handler, event, data):
        redis = await AsyncRedisClient.get_client()
        user_id = getattr(event, "from_user", None)
        if user_id is None:
            return await handler(event, data)

        key = f"rate:{user_id.id}"
        current = await redis.get(key)
        current = int(current) if current else 0

        if current >= self.limit:
            if isinstance(event, Message):
                await event.answer("⏳ Слишком часто, подожди!")
            elif isinstance(event, CallbackQuery):
                await event.answer("⏳ Слишком часто, подожди!", show_alert=True)
            return

        async with redis.pipeline(transaction=True) as pipe:
            await pipe.incr(key)
            await pipe.expire(key, self.period)
            await pipe.execute()

        return await handler(event, data)
