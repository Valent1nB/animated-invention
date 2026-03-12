from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.health.healch_check_use_case import HealthCheckUseCase
from app.infrastructure.repositories.health_check_repository_impl import HealthCheckRepository
from app.presentation.dependencies.db import get_async_session


def get_health_check_use_case(db_session: Annotated[AsyncSession, Depends(get_async_session)]) -> HealthCheckUseCase:
    repo = HealthCheckRepository(db_session=db_session)
    return HealthCheckUseCase(repo=repo)
