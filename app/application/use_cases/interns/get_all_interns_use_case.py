from app.common.list import ListResult
from app.domain.entities.employee.intern import InternListFilters, InternOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetAllInternsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, filters: InternListFilters, employee: MentorProfile | None = None
    ) -> ListResult[InternOut]:
        return await self._uow.interns.list(filters, employee=employee)
