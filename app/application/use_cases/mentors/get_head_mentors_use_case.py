from uuid import UUID

from app.common.list import ListResult
from app.domain.entities.employee.mentor import MentorOut
from app.domain.unit_of_work import IUnitOfWork


class GetHeadMentorsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, unit_id: UUID | None = None) -> ListResult[MentorOut]:
        return await self._uow.mentors.get_head_mentors(unit_id=unit_id)
