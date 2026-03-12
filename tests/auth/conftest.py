import pytest
from httpx_oauth.oauth2 import OAuth2Token
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories.auth import UserFactory
from tests.factories.mentor import MentorFactory


@pytest.fixture
async def test_mentor_for_intern_auth(async_session: AsyncSession):
    mentor = MentorFactory()
    if mentor not in async_session:
        async_session.add(mentor)

    await async_session.flush()
    return mentor


@pytest.fixture
async def test_mentor_for_intern_auth_no_user(async_session: AsyncSession):
    mentor = MentorFactory(user=None)
    if mentor not in async_session:
        async_session.add(mentor)
    await async_session.flush()
    return mentor


@pytest.fixture
async def user_for_mentor_email(test_mentor_for_intern_auth):
    user = test_mentor_for_intern_auth.user
    return user


@pytest.fixture
async def user_with_new_email(async_session: AsyncSession):
    user = UserFactory(email="newuser@example.com")
    if user not in async_session:
        async_session.add(user)
    await async_session.flush()
    return user


@pytest.fixture
async def user_with_nonexistent_email(async_session: AsyncSession):
    user = UserFactory(email="nonexistent@example.com")
    if user not in async_session:
        async_session.add(user)
    await async_session.flush()
    return user


@pytest.fixture
def mock_oauth_token():
    return OAuth2Token(
        {"access_token": "test_access_token", "refresh_token": "test_refresh_token", "expires_in": 3600},
    )
