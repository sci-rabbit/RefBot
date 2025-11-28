from typing import List

from aiogram.types import InputMediaPhoto

from core.media_utils import get_media
from core.models import Message


def prepared_media(
    media_group: List[Message],
) -> List[InputMediaPhoto] | List[Message]:
    prepared_media_group = []

    for media in media_group:
        if media.token_file:
            prepared_media_group.append(
                InputMediaPhoto(
                    media=media.token_file,
                    caption=media.hash_tags,
                )
            )
            continue

        if media.photo:
            file_bytes = media.photo
            if file_bytes:
                prepared_media_group.append(
                    get_media(caption=media.hash_tags, raw_bytes=file_bytes)
                )

    return prepared_media_group
