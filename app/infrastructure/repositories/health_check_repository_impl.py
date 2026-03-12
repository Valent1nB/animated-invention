from time import perf_counter

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.health import CheckResult, Status
from app.domain.repositories.health_repository import IHealthCheckRepository


class HealthCheckRepository(IHealthCheckRepository):
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def db_health_check(self) -> CheckResult:
        time_start = perf_counter()

        async with self.db_session as session:
            try:
                await session.execute(text("SELECT 1;"))
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to execute DB health check: {e}")
                return CheckResult(
                    status=Status.FAILED,
                    time=perf_counter() - time_start,
                    info=str(e),
                )
            else:
                return CheckResult(
                    status=Status.OK,
                    time=perf_counter() - time_start,
                )
