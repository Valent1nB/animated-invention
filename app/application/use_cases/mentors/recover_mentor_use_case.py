from uuid import UUID

from app.domain.entities.employee.mentor import MentorOut
from app.domain.unit_of_work import IUnitOfWork


class RecoverMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, mentor_id: UUID, commit: bool = False) -> MentorOut | None:
        mentor = await self._uow.mentors.recover(mentor_id)
        if commit:
            await self._uow.commit()

        return mentor
