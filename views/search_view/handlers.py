import asyncio

import structlog
from aiogram.exceptions import TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.search_kb import get_inline_search_kb
from core.media_utils import send_media
from core.services.search_service import SearchService

logger = structlog.getLogger(__name__)


async def search_messages_handler(
    bot,
    session: AsyncSession,
    search: str,
    chat_id: int,
    limit: int = 30,
    offset: int = 0,
) -> None:
    search_service = SearchService(session=session)
    media_groups = await search_service.get_messages(
        search=search,
        limit=limit,
        offset=offset,
    )

    for media_group in media_groups:
        try:
            await send_media(bot, media_group, chat_id)
        except TelegramRetryAfter as e:
            logger.warning("Telegram Retry - Flood wait", time=e.retry_after)
            await asyncio.sleep(e.retry_after)
            await send_media(bot, media_group, chat_id)


async def send_results(
    bot,
    session: AsyncSession,
    search: str,
    message,
    state=None,
    offset: int = 0,
    page_size: int = 30,
):
    logger.info(
        "Начало отправки результатов chat_id=%r, offset=%r, page_size=%r",
        message.chat.id,
        offset,
        page_size,
    )

    media_groups = await SearchService(session=session).get_messages(
        search=search,
        limit=page_size + 1,
        offset=offset,
    )

    has_next = len(media_groups) > page_size

    await search_messages_handler(
        bot=bot,
        session=session,
        search=search,
        chat_id=message.chat.id,
        limit=page_size,
        offset=offset,
    )

    if has_next:
        next_offset = offset + page_size
        await message.answer(
            "Есть ещё сообщения, хотите продолжить?",
            reply_markup=get_inline_search_kb(next_offset),
        )
    else:
        if state:
            await state.clear()
        await message.answer("✅ Это всё!")

    logger.info(
        "Отправка результатов завершена, chat_id=%r, offset=%r, total_fetched=%r",
        message.chat.id,
        offset,
        len(media_groups),
    )
