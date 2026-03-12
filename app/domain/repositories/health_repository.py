from abc import ABC, abstractmethod

from app.domain.entities.health import CheckResult


class IHealthCheckRepository(ABC):
    @abstractmethod
    async def db_health_check(self) -> CheckResult:
        raise NotImplementedError
