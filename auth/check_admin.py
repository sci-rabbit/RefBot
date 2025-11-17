import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config import settings

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        logger.info(
            "Пользователь %r запросил доступ к защищённому ресурсу",
            message.from_user,
        )
        result_bool = message.from_user.id in settings.bot.admin_ids

        if not result_bool:
            await message.answer("❌У вас нет прав для этого действия")
            logger.info(
                "❌В доступе отказано для пользователя %r",
                message.from_user,
            )
        return result_bool


async def send_notification_to_admin(
    bot,
    redis,
    admin_ids=settings.bot.admin_ids,
):
    keys = await redis.keys("suggestion:*")
    count = len(keys)

    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"📬 Новая предложка добавлена!\n" f"📦 Всего предложек: {count}",
        )
