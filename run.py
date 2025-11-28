import asyncio
import logging

import structlog
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.db.database import dispose
from core.db.db_filler import db_filler
from error_handler import register_error_handlers, setup_async_exception_handler
from health_monitors import health_monitor_task, _check_db
from middleware import rate_middleware
from redis_client.redis import set_async_redis_client, redis_client_close
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

dp.message.middleware(rate_middleware)
dp.callback_query.middleware(rate_middleware)


async def on_startup() -> None:
    await set_async_redis_client()
    await tg_client.start()
    logger.info("Startup completed")

    db_ok = await _check_db()
    if db_ok:
        asyncio.create_task(
            db_filler(
                client=tg_client,
            )
        )


async def on_shutdown():
    await tg_client.disconnect()
    await redis_client_close()
    await dispose()
    logger.info("Shutdown completed")


async def main():
    register_error_handlers(dp)
    dp.include_router(router)

    stop_event = asyncio.Event()
    health_task = asyncio.create_task(health_monitor_task(stop_event))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot)
    finally:
        stop_event.set()
        await health_task


if __name__ == "__main__":
    setup_async_exception_handler(asyncio.get_event_loop())
    asyncio.run(main())
