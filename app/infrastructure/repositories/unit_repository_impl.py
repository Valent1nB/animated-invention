from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.employee.employee import UnitOut
from app.domain.repositories.unit_repository import IUnitRepository
from app.infrastructure.database.models.unit import Unit as UnitORM


class UnitRepository(IUnitRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_all(self) -> list[UnitOut]:
        stmt = select(UnitORM).order_by(UnitORM.name)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [UnitOut.model_validate(row) for row in rows]
