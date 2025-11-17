import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from error_handler import register_error_handlers, setup_async_exception_handler
from middleware import RateLimitMiddleware
from redis_client.redis import set_async_redis_client
from src.bot import bot
from src.tg_client import tg_client
from views import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("/app/logs/bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger()

dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(RateLimitMiddleware(limit=7, period=10))
dp.callback_query.middleware(RateLimitMiddleware(limit=7, period=10))


async def on_startup() -> None:
    await set_async_redis_client()
    await tg_client.start()


async def on_shutdown():
    await tg_client.disconnect()


async def main():
    register_error_handlers(dp)
    dp.include_router(router=router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    setup_async_exception_handler(loop)
    loop.run_until_complete(main())
