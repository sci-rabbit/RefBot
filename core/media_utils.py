from io import BytesIO
from typing import List

import telethon
from aiogram import Bot
from aiogram.types import BufferedInputFile, InputMediaPhoto


async def download_media(msg: telethon.tl.custom.message.Message):
    bio = BytesIO()
    await msg.download_media(file=bio)
    bio.seek(0)
    raw_bytes = bio.read()
    return raw_bytes


def get_media(caption: str, raw_bytes: bytes):
    file = BufferedInputFile(raw_bytes, filename="file")
    return InputMediaPhoto(caption=caption, media=file)


async def send_media(
    bot: Bot,
    messages: List[InputMediaPhoto],
    chat_id: int,
):
    await bot.send_media_group(chat_id=chat_id, media=messages)
