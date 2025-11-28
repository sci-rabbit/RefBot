from typing import List

import structlog
from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Message
from core.repositories.search_repository import SearchRepository

from core.services.utils import prepared_media

logger = structlog.getLogger(__name__)


class SearchService:
    def __init__(self, session: AsyncSession):
        self.repo = SearchRepository(session=session)
        self.albums: List[List[InputMediaPhoto] | List[Message]] = []

    async def get_messages(
        self,
        search: str,
        limit: int = 30,
        offset: int = 0,
    ) -> List[List[InputMediaPhoto] | List[Message]]:
        matched = await self.repo.get_messages_by_search(
            search=search,
            limit=limit,
            offset=offset,
        )

        if not matched:
            return self.albums

        for match in matched:
            media_group = [match]
            if match.media_group_id:
                media_group = await self.repo.get_messages_by_media_group(
                    match.media_group_id
                )
            try:
                prepared_media_group = prepared_media(media_group)
            except Exception as e:
                logger.error(
                    "Ошибка во время подготовки медиа", error=str(e), exc_info=True
                )
                prepared_media_group = []
            self.albums.append(prepared_media_group)

        return self.albums
