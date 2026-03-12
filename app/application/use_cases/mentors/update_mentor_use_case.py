from uuid import UUID

from app.domain.entities.employee.mentor import MentorOut, MentorUpdate
from app.domain.unit_of_work import IUnitOfWork


class UpdateMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, mentor_id: UUID, mentor_update: MentorUpdate, commit: bool = False) -> MentorOut | None:
        updated_mentor = await self._uow.mentors.update(mentor_id, mentor_update)
        if commit:
            await self._uow.commit()

        return updated_mentor
