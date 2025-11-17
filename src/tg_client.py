import asyncio
from telethon import TelegramClient

from config import settings

tg_client = TelegramClient(
    api_id=settings.tg_client.api_id,
    api_hash=settings.tg_client.api_hash,
    session=settings.tg_client.session,
)