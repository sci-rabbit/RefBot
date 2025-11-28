from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Message
from core.repositories.new_reference_repository import ReferenceRepository


class ReferenceService:
    def __init__(self, session: AsyncSession):
        self.repo = ReferenceRepository(session=session)

    async def create_new_ref_with_token_file(self, data: dict) -> Message:
        return await self.repo.create(data)
