from typing import List
import re

from sqlalchemy import select, true, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.messages import Message


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_messages_by_search(
        self,
        search: str,
        limit: int = 30,
        offset: int = 0,
    ) -> List[Message]:
        stmt = (
            select(Message)
            .where(self.match_message_sql(search, Message.hash_tags))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_messages_by_media_group(self, media_group_id: int) -> List[Message]:
        stmt = select(Message).where(Message.media_group_id == media_group_id)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    def match_message_sql(search: str, column):
        if not search:
            return true()

        words = [w.lstrip("#") for w in search.lower().split() if w.startswith("#")]

        exprs = []
        for w in words:
            safe = re.escape(w)
            pattern = rf"#\w*{safe}\w*"
            exprs.append(column.op("~*")(pattern))

        return and_(*exprs)
