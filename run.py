import asyncio
import logging

import structlog
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.db.database import get_session
from core.db.db_filler import db_filler
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
        logging.StreamHandler(),
        logging.FileHandler("/app/logs/bot.log", encoding="utf-8"),
    ],
)

logger = structlog.getLogger(__name__)

dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(RateLimitMiddleware())
dp.callback_query.middleware(RateLimitMiddleware())


async def on_startup() -> None:
    await set_async_redis_client()
    await tg_client.start()
    logger.info("ТГ клиент успешно запущен")
    logger.info()
    async with get_session() as session:
        await db_filler(
            session=session,
            client=tg_client,
        )


async def on_shutdown():
    await tg_client.disconnect()
    logger.info("ТГ клиент успешно завершён")


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
