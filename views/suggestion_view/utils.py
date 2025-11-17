import json
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaDocument


async def process_state_photo(
    message: Message, state: FSMContext
) -> (dict[str, Any], list):
    data = await state.get_data()
    media_group = data.get("waiting_for_photos", {})

    if "caption" not in media_group and message.caption:
        media_group["caption"] = message.caption

    if message.photo:
        photos = media_group.get("photos", [])
        photos.append(message.photo[-1].file_id)
        media_group["photos"] = photos
        return media_group, photos

    if message.document:
        documents = media_group.get("documents", [])
        documents.append(message.document.file_id)
        media_group["documents"] = documents
        return media_group, documents


def collect_media(data: str | bytearray):
    media_group = json.loads(data)

    photos = media_group.get("photos", [])
    documents = media_group.get("documents", [])
    caption = media_group.get("caption", "")

    media = []

    if photos:
        # Фото
        for i, photo in enumerate(photos):
            media.append(
                InputMediaPhoto(
                    media=photo,
                    caption=caption if i == 0 and not documents else None,
                )
            )

    if documents:
        # Документы
        for i, doc in enumerate(documents):
            media.append(
                InputMediaDocument(
                    media=doc,
                    caption=caption if i == 0 and not photos else None,
                )
            )

    return media
