import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from app.domain.entities.employee.enum import Role


@pytest.mark.asyncio
async def test_get_profile_as_superuser(superuser_client: AsyncClient):
    response = await superuser_client.get("/api/v1/mentor/me")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()

    assert json_data.get("email") == "superuser@example.com"
    assert json_data.get("role") == Role.superuser


@pytest.mark.asyncio
async def test_get_profile_as_head_mentor(head_mentor_client: AsyncClient):
    response = await head_mentor_client.get("/api/v1/mentor/me")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()

    assert json_data.get("email") == "head_mentor@example.com"
    assert json_data.get("role") == Role.head_mentor


@pytest.mark.asyncio
async def test_get_profile_as_mentor(mentor_client: AsyncClient):
    response = await mentor_client.get("/api/v1/mentor/me")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()

    assert json_data.get("email") == "mentor@example.com"
    assert json_data.get("role") == Role.mentor


@pytest.mark.asyncio
async def test_get_profile_unauthorized(unauthorized_client: AsyncClient):
    response = await unauthorized_client.get("/api/v1/mentor/me")
    assert response.status_code == HTTP_401_UNAUTHORIZED
