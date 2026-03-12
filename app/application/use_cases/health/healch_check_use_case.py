from app.domain.entities.health import CheckResult
from app.domain.repositories.health_repository import IHealthCheckRepository


class HealthCheckUseCase:
    def __init__(self, repo: IHealthCheckRepository) -> None:
        self._repo = repo

    async def db_health(self) -> CheckResult:
        return await self._repo.db_health_check()
