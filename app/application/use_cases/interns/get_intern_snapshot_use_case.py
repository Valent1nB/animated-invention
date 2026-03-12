from app.domain.entities.employee.intern import InternSnapshotFilters, InternStatsOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetInternSnapshotUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, filters: InternSnapshotFilters, employee: MentorProfile | None = None) -> InternStatsOut:
        return await self._uow.interns.get_snapshot_stats(filters, employee=employee)
