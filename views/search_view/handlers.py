import logging
from collections import defaultdict

from config import settings
from core.keyboards.search_kb import get_inline_search_kb
from views.search_view.utils import send_media, match_messages

logger = logging.getLogger(__name__)


async def search_message_processor(
    client,
    search,
    limit,
    offset_id,
    source_chat: int = settings.bot.source_chat,
):
    albums = defaultdict(list)
    grouped_ids = set()

    logger.info(
        "🔍 Начало поиска: search=%r, offset=%r, limit=%r, chat=%r",
        search,
        offset_id,
        limit,
        source_chat,
    )

    async for msg in client.iter_messages(
        source_chat,
        limit=limit,
        offset_id=offset_id,
        reverse=True,
    ):
        match = await match_messages(search, msg)
        logger.debug(
            f"MSG %r group=%r match=%r media=%r",
            msg.id,
            msg.grouped_id,
            match,
            bool(msg.media),
        )
        if not msg.media:
            continue

        group_id = msg.grouped_id or msg.id
        if match or group_id in grouped_ids:
            grouped_ids.add(group_id)
            albums[group_id].append(msg)

    logger.info("✅ Поиск завершён: собрано %r сообщений", len(albums))

    return albums


async def send_results(
    bot,
    albums,
    message,
    state=None,
    count: int = 0,
):
    keys = list(albums.keys())
    end = min(count + 50, len(keys))

    logger.info(
        "Начало отправки результатов %r, Счётчик пагинации: count=%r end=%r",
        message.chat.id,
        count,
        end,
    )
    for i in range(count, end):
        count += 1
        await send_media(
            bot,
            albums[keys[i]],
            message.chat.id,
        )
    count = end
    logger.debug(
        "Отправка медиа завершена, sent_count=%r",
        count,
    )
    if 0 < count < len(keys):
        await message.answer(
            "Есть ещё сообщения, хотите продолжить?",
            reply_markup=get_inline_search_kb(
                count,
            ),
        )
    else:
        if state:
            await state.clear()
        await message.answer("✅ Это всё!")

    logger.info(
        "Отправка результатов завершена, %r",
        message.chat.id,
    )
