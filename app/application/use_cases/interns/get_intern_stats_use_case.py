from app.domain.entities.employee.intern import InternStatsFilters, InternStatsOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetInternStatsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, filters: InternStatsFilters, employee: MentorProfile | None = None) -> InternStatsOut:
        return await self._uow.interns.get_status_stats(filters, employee=employee)
