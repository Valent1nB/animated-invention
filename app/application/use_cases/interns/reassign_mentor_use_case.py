from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.domain.entities.employee.intern import InternOut
from app.domain.unit_of_work import IUnitOfWork


class ReassignMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self,
        intern_id: UUID,
        new_mentor_id: UUID,
        commit: bool = False,
    ) -> InternOut | None:
        mentor = await self._uow.mentors.get_one(new_mentor_id)
        if mentor is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Mentor not found")

        if not mentor.available:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Mentor is archived")

        updated_intern = await self._uow.interns.reassign_mentor(intern_id, new_mentor_id)
        if commit:
            await self._uow.commit()

        return updated_intern
