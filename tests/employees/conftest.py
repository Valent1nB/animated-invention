import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.intern import InternFactory
from tests.factories.mentor import MentorFactory


@pytest.fixture
async def test_mentor_for_avatar(async_session: AsyncSession):
    mentor = MentorFactory()
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def other_mentor_for_avatar(async_session: AsyncSession):
    mentor = MentorFactory()
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def test_intern_for_avatar(async_session: AsyncSession, test_mentor_for_avatar):
    intern = InternFactory(mentor=test_mentor_for_avatar)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def intern_with_other_mentor(async_session: AsyncSession, other_mentor_for_avatar):
    intern = InternFactory(mentor=other_mentor_for_avatar)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def mentor_with_avatar(async_session: AsyncSession):
    mentor = MentorFactory(avatar_key="avatars/old_avatar.png")
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def intern_with_avatar(async_session: AsyncSession, test_mentor_for_avatar):
    intern = InternFactory(mentor=test_mentor_for_avatar, avatar_key="avatars/old_intern_avatar.png")
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern


@pytest.fixture
async def intern_for_logged_in_mentor(async_session: AsyncSession, mentor):
    intern = InternFactory(mentor=mentor)
    if intern not in async_session:
        async_session.add(intern)
    await async_session.flush()
    return intern
