from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.domain.entities.employee.intern import InternIn, InternOut
from app.domain.unit_of_work import IUnitOfWork


class CreateInternUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, intern_schema: InternIn, commit: bool = False) -> InternOut:
        mentor = await self._uow.mentors.get_one(intern_schema.mentor_id)
        if mentor is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Mentor not found")

        if not mentor.available:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Mentor is archived")

        created_intern = await self._uow.interns.create(intern_schema)
        if commit:
            await self._uow.commit()

        return created_intern
