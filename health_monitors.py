import asyncio

import structlog

from core.db.database import get_session
from redis_client.redis import AsyncRedisClient
from src.tg_client import tg_client

logger = structlog.getLogger(__name__)


async def _check_redis() -> bool:
    redis = await AsyncRedisClient().get_client()
    if not redis:
        return False
    try:
        await redis.ping()
        return True
    except Exception:
        return False


async def _check_db() -> bool:
    try:
        async with get_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception:
        return False


async def _check_telethon() -> bool:
    try:
        return tg_client.is_connected()
    except Exception:
        return False


async def health_monitor_task(stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            redis_ok = await _check_redis()
            db_ok = await _check_db()
            telethon_ok = await _check_telethon()

            if not all((redis_ok, db_ok, telethon_ok)):
                logger.warning(
                    "Health check failed",
                    redis=redis_ok,
                    db=db_ok,
                    telethon=telethon_ok,
                )
            await asyncio.wait_for(stop_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            continue
        except Exception:
            logger.exception("Unexpected error in health monitor")
            await asyncio.sleep(5)
