from app.domain.entities.employee.employee import UnitOut
from app.domain.unit_of_work import IUnitOfWork


class GetUnitsUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def __call__(self) -> list[UnitOut]:
        return await self._uow.units.list_all()
