from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.unit_of_work import IUnitOfWork
from app.infrastructure.unit_of_work import UnitOfWork
from app.presentation.dependencies.db import get_async_session


async def get_unit_of_work(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AsyncGenerator[IUnitOfWork, None]:
    async with UnitOfWork(existing_session=session) as uow:
        yield uow
