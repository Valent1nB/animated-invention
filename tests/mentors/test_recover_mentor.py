from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)


@pytest.mark.asyncio
async def test_recover_mentor_as_superuser(superuser_client: AsyncClient, archived_mentor):
    response = await superuser_client.patch(f"/api/v1/mentor/{archived_mentor.id}/recover")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("id") == str(archived_mentor.id)
    assert json_data.get("available") is True


@pytest.mark.asyncio
async def test_recover_mentor_as_head_mentor(head_mentor_client: AsyncClient, archived_mentor):
    response = await head_mentor_client.patch(f"/api/v1/mentor/{archived_mentor.id}/recover")
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("available") is True


@pytest.mark.asyncio
async def test_recover_mentor_as_mentor_forbidden(mentor_client: AsyncClient, archived_mentor):
    response = await mentor_client.patch(f"/api/v1/mentor/{archived_mentor.id}/recover")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_recover_self_forbidden(head_mentor, head_mentor_client: AsyncClient):
    response = await head_mentor_client.patch(f"/api/v1/mentor/{head_mentor.id}/recover")
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == "Cannot recover self"


@pytest.mark.asyncio
async def test_recover_mentor_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    response = await superuser_client.patch(f"/api/v1/mentor/{non_existent_id}/recover")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Mentor not found"


@pytest.mark.asyncio
async def test_recover_mentor_unauthorized(unauthorized_client: AsyncClient):
    mentor_id = uuid4()
    response = await unauthorized_client.patch(f"/api/v1/mentor/{mentor_id}/recover")
    assert response.status_code == HTTP_401_UNAUTHORIZED
