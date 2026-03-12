from uuid import UUID

from app.domain.entities.employee.intern import InternOut
from app.domain.unit_of_work import IUnitOfWork


class GetInternUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, intern_id: UUID) -> InternOut | None:
        intern = await self._uow.interns.get_one(intern_id)

        return intern
