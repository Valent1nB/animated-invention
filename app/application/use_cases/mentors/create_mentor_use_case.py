from app.domain.entities.employee.mentor import MentorOut, ShortMentorIn
from app.domain.unit_of_work import IUnitOfWork


class CreateMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, mentor_schema: ShortMentorIn, commit: bool = False) -> MentorOut:
        created_mentor = await self._uow.mentors.create_without_user(mentor_schema)
        if commit:
            await self._uow.commit()

        return created_mentor
