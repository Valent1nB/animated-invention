import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from app.app import app
from app.config import config
from app.domain.entities.employee.enum import Role
from app.infrastructure.database import Base
from app.presentation.auth_backend import current_active_user
from app.presentation.dependencies.db import get_async_session
from tests.factories.auth import UserFactory
from tests.factories.base import BaseFactory
from tests.factories.intern import InternFactory
from tests.factories.mentor import MentorFactory
from tests.factories.request import RequestFactory
from tests.factories.unit import UnitFactory


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    db_url = f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.PGPASSWORD}@{config.PGHOST}:{config.PGPORT}/px_test"

    engine = create_async_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=False,
        future=True,
    )

    yield engine
    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_database(async_engine: AsyncEngine):
    admin_engine = create_async_engine(
        config.DB_URL,
        isolation_level="AUTOCOMMIT",
    )

    async with admin_engine.connect() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS px_test"))
        await conn.execute(text("CREATE DATABASE px_test"))

    await admin_engine.dispose()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_session(async_engine: AsyncEngine):
    async with async_engine.connect() as connection:
        trans = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autoflush=False,
        )

        await session.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(sess, transaction):
            if transaction.nested and not sess.in_nested_transaction():
                sess.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture(autouse=True)
def set_session(async_session: AsyncSession):
    BaseFactory.set_session(async_session)
    UnitFactory.set_session(async_session)
    MentorFactory.set_session(async_session)
    InternFactory.set_session(async_session)
    UserFactory.set_session(async_session)
    RequestFactory.set_session(async_session)


@pytest.fixture
async def override_dependency(
    async_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    async def _override_get_async_session():
        yield async_session

    app.dependency_overrides[get_async_session] = _override_get_async_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def default_unit(async_session: AsyncSession):
    unit = UnitFactory(name="Default")
    if unit not in async_session:
        async_session.add(unit)
    await async_session.flush()
    return unit


@pytest.fixture
async def another_unit(async_session: AsyncSession):
    unit = UnitFactory(name="Other Unit")
    if unit not in async_session:
        async_session.add(unit)
    await async_session.flush()
    return unit


@pytest.fixture
async def superuser(async_session: AsyncSession, default_unit):
    superuser = MentorFactory(
        role=Role.superuser,
        email="superuser@example.com",
        unit=default_unit,
    )

    await async_session.flush()
    return superuser


@pytest.fixture
async def head_mentor(async_session: AsyncSession, default_unit):
    head_mentor = MentorFactory(
        role=Role.head_mentor,
        email="head_mentor@example.com",
        unit=default_unit,
    )

    await async_session.flush()
    return head_mentor


@pytest.fixture
async def mentor(async_session: AsyncSession, default_unit):
    mentor = MentorFactory(
        role=Role.mentor,
        email="mentor@example.com",
        unit=default_unit,
    )

    await async_session.flush()
    return mentor


@pytest.fixture
async def unauthorized_client(override_dependency):
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def superuser_client(superuser, override_dependency, async_session: AsyncSession):
    async def _override_current_active_user():
        return superuser.user

    app.dependency_overrides[current_active_user] = _override_current_active_user

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.pop(current_active_user, None)


@pytest.fixture
async def head_mentor_client(
    head_mentor,
    override_dependency,
):
    async def _override_current_active_user():
        return head_mentor.user

    app.dependency_overrides[current_active_user] = _override_current_active_user

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.pop(current_active_user, None)


@pytest.fixture
async def mentor_client(
    mentor,
    override_dependency,
):
    async def _override_current_active_user():
        return mentor.user

    app.dependency_overrides[current_active_user] = _override_current_active_user

    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.pop(current_active_user, None)
