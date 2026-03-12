from uuid import UUID

from app.domain.entities.employee.intern import InternOut, InternUpdate
from app.domain.unit_of_work import IUnitOfWork


class UpdateInternUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self, intern_id: UUID, intern_update: InternUpdate, commit: bool = False) -> InternOut | None:
        updated_intern = await self._uow.interns.update(intern_id, intern_update)
        if commit:
            await self._uow.commit()

        return updated_intern
