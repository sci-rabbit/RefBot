import structlog
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from core.media_utils import download_media
from core.models.messages import Message
from telethon import TelegramClient

logger = structlog.getLogger(__name__)


async def db_filler(
    session: AsyncSession,
    client: TelegramClient,
    source_chat: int = settings.bot.source_chat,
) -> None:
    logger.info(
        "DB_FILLER: Заполнение базы данных началось",
    )

    logger.info(
        "🔍 Начало поиска: chat=%r",
        source_chat,
    )
    async for msg in client.iter_messages(
        source_chat,
    ):
        logger.debug(
            "Найдено сообщение message_id=%s",
            msg.id,
        )
        if msg.media:
            try:
                msg_photo_bytes = await download_media(msg)
                message = Message(
                    message_id=msg.id,
                    media_group_id=msg.grouped_id,
                    hash_tags=msg.message,
                    photo=msg_photo_bytes,
                )
                session.add(message)
                await session.commit()
            except (
                DataError,
                StatementError,
                IntegrityError,
            ) as e:
                logger.exception(
                    "Ошибка базы данных во время добавления элементов",
                    error=str(e),
                    exc_info=True,
                )
                await session.rollback()
                continue

    logger.info("✅ Поиск завершён")
    logger.info(
        "✅DB_FILLER: Заполнение базы данных завершилось успешно",
    )
