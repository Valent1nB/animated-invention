from abc import ABC, abstractmethod

from app.domain.entities.employee.employee import UnitOut


class IUnitRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[UnitOut]:
        raise NotImplementedError
