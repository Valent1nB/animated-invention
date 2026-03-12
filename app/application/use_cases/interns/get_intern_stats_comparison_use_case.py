from app.domain.entities.employee.intern import (
    InternStatsComparisonFilters,
    InternStatsComparisonOut,
    InternStatsFilters,
)
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetInternStatsComparisonUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, filters: InternStatsComparisonFilters, employee: MentorProfile | None = None
    ) -> InternStatsComparisonOut:
        current_stats = await self._uow.interns.get_status_stats(
            InternStatsFilters(
                statuses=filters.statuses,
                mentor_id=filters.mentor_id,
                period=filters.current_period,
            ),
            employee=employee,
        )

        previous_stats = await self._uow.interns.get_status_stats(
            InternStatsFilters(
                statuses=filters.statuses,
                mentor_id=filters.mentor_id,
                period=filters.previous_period,
            ),
            employee=employee,
        )

        absolute_change = current_stats.total - previous_stats.total
        percent_change = None
        if previous_stats.total != 0:
            percent_change = (absolute_change / previous_stats.total) * 100

        return InternStatsComparisonOut(
            current=current_stats,
            previous=previous_stats,
            absolute_change=absolute_change,
            percent_change=percent_change,
        )
