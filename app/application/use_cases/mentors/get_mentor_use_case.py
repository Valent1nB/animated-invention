from uuid import UUID

from app.domain.entities.employee.mentor import MentorOut
from app.domain.unit_of_work import IUnitOfWork


class GetMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, mentor_id: UUID) -> MentorOut | None:
        mentor = await self._uow.mentors.get_one(mentor_id)

        return mentor
