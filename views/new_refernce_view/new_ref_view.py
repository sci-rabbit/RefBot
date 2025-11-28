import structlog
from aiogram import Router, F
from aiogram.types import Message

from core.db.database import get_session
from core.services.new_ref_service import ReferenceService

logger = structlog.getLogger(__name__)


new_ref_router = Router()


@new_ref_router.channel_post(F.photo)
async def channel_photo_handler(message: Message):

    data_to_save = dict()

    data_to_save["token_file"] = message.photo[-1].file_id
    print(message.caption)
    data_to_save["hash_tags"] = message.caption
    data_to_save["media_group_id"] = int(message.media_group_id)
    data_to_save["message_id"] = message.message_id
    async with get_session() as session:
        ref_service = ReferenceService(session=session)
        obj = await ref_service.create_new_ref_with_token_file(data_to_save)
    if obj:
        logger.debug("New added object", object=obj)
        logger.info("Объект успешно добавлен в базу данных")
