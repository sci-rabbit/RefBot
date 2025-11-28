from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Message


class ReferenceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Message | None:
        new_msg = Message(**data)
        self.session.add(new_msg)
        return new_msg
