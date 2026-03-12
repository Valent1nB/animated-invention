from app.common.list import ListResult
from app.domain.entities.employee.mentor import MentorListFilters, MentorOut
from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.database import MentorProfile


class GetAllMentorsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(
        self, filters: MentorListFilters, employee: MentorProfile | None = None
    ) -> ListResult[MentorOut]:
        return await self._uow.mentors.list(filters, employee=employee)
