from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.infrastructure.database import MentorProfile as MentorProfileORM


@pytest.mark.asyncio
async def test_get_mentor_as_superuser(superuser_client: AsyncClient, test_mentor):
    response = await superuser_client.get(f"/api/v1/mentor/{test_mentor.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_mentor.id)
    assert json_data.get("email") == test_mentor.email


@pytest.mark.asyncio
async def test_get_mentor_as_head_mentor(head_mentor_client: AsyncClient, test_mentor):
    response = await head_mentor_client.get(f"/api/v1/mentor/{test_mentor.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_mentor.id)


@pytest.mark.asyncio
async def test_get_mentor_as_mentor_self(mentor_client: AsyncClient, async_session: AsyncSession):
    result = await async_session.execute(select(MentorProfileORM).where(MentorProfileORM.email == "mentor@example.com"))
    mentor = result.scalar_one()

    response = await mentor_client.get(f"/api/v1/mentor/{mentor.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(mentor.id)


@pytest.mark.asyncio
async def test_get_mentor_as_mentor(mentor_client: AsyncClient, test_mentor):
    response = await mentor_client.get(f"/api/v1/mentor/{test_mentor.id}")
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_mentor_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    response = await superuser_client.get(f"/api/v1/mentor/{non_existent_id}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Mentor not found"


@pytest.mark.asyncio
async def test_get_mentor_unauthorized(unauthorized_client: AsyncClient):
    mentor_id = uuid4()
    response = await unauthorized_client.get(f"/api/v1/mentor/{mentor_id}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
