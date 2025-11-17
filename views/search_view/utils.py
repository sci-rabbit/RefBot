import asyncio
import logging
import re
from io import BytesIO

import telethon
from aiogram.types import BufferedInputFile, InputMediaPhoto, Message
from aiogram import Bot


logger = logging.getLogger(__name__)

SEM = asyncio.Semaphore(5)


async def get_media(msg: telethon.tl.custom.message.Message):
    async with SEM:
        bio = BytesIO()
        try:
            await msg.download_media(file=bio)

            bio.seek(0)
            file = BufferedInputFile(bio.read(), filename="file")
            media = InputMediaPhoto(caption=msg.text, media=file)
            return media
        finally:
            bio.close()


async def match_messages(search: str, msg: Message) -> bool:
    if not search:
        return True

    text = (msg.message or "").lower()

    words = [w.lstrip("#") for w in search.lower().split() if w.startswith("#")]
    logger.debug(
        "Match messages process search_value=%r, message_text=%r, res_words=%r",
        search,
        text,
        words,
    )
    return all(re.search(rf"#\w*{re.escape(word)}\w*", text) for word in words)


async def send_media(
    bot: Bot,
    messages: list[telethon.tl.custom.message.Message],
    chat_id: int,
):

    tasks = [asyncio.create_task(get_media(message)) for message in messages]

    media_list = await asyncio.gather(*tasks, return_exceptions=True)
    for exc in media_list:
        if isinstance(exc, Exception):
            logger.exception(
                "Ошибка выполнения задачи скачивания медиа",
                repr(exc),
            )
    await bot.send_media_group(chat_id=chat_id, media=media_list)
