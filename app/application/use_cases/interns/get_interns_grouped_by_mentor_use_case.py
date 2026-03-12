from app.domain.entities.employee.intern import InternGroupedByMentorResponse, InternListFilters
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetInternsGroupedByMentorUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, filters: InternListFilters, employee: MentorProfile | None = None
    ) -> InternGroupedByMentorResponse:
        return await self._uow.interns.list_grouped_by_mentor(filters, employee=employee)
