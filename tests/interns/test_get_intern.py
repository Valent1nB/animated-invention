from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from app.infrastructure.database.models.employee import InternProfile as InternProfileORM


@pytest.mark.asyncio
async def test_get_intern_as_superuser(superuser_client: AsyncClient, test_intern):
    response = await superuser_client.get(f"/api/v1/intern/{test_intern.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_intern.id)
    assert json_data.get("email") == test_intern.email


@pytest.mark.asyncio
async def test_get_intern_as_head_mentor(head_mentor_client: AsyncClient, test_intern):
    response = await head_mentor_client.get(f"/api/v1/intern/{test_intern.id}")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(test_intern.id)


@pytest.mark.asyncio
async def test_get_intern_as_mentor_own_intern(mentor_client: AsyncClient, async_session: AsyncSession):
    from app.infrastructure.database import MentorProfile as MentorProfileORM

    result = await async_session.execute(select(MentorProfileORM).where(MentorProfileORM.email == "mentor@example.com"))
    mentor = result.scalar_one_or_none()

    if mentor:
        intern = InternProfileORM(
            first_name="Test",
            last_name="Intern",
            email="test_intern_own@example.com",
            mentor_id=mentor.id,
            unit_id=mentor.unit_id,
        )
        async_session.add(intern)
        await async_session.flush()

        response = await mentor_client.get(f"/api/v1/intern/{intern.id}")
        assert response.status_code == HTTP_200_OK

        json_data = response.json()
        assert json_data.get("id") == str(intern.id)


@pytest.mark.asyncio
async def test_get_intern_as_mentor_other_intern(mentor_client: AsyncClient, other_intern):
    response = await mentor_client.get(f"/api/v1/intern/{other_intern.id}")
    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_intern_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    response = await superuser_client.get(f"/api/v1/intern/{non_existent_id}")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Intern not found"


@pytest.mark.asyncio
async def test_get_intern_unauthorized(unauthorized_client: AsyncClient):
    intern_id = uuid4()
    response = await unauthorized_client.get(f"/api/v1/intern/{intern_id}")
    assert response.status_code == HTTP_401_UNAUTHORIZED
