from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_mentor_as_superuser(superuser_client: AsyncClient, test_mentor):
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "city": "New City",
    }
    response = await superuser_client.patch(f"/api/v1/mentor/{test_mentor.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("first_name") == "Updated"
    assert json_data.get("last_name") == "Name"
    assert json_data.get("city") == "New City"


@pytest.mark.asyncio
async def test_update_mentor_as_head_mentor(head_mentor_client: AsyncClient, test_mentor):
    update_data = {"first_name": "HeadUpdated"}
    response = await head_mentor_client.patch(f"/api/v1/mentor/{test_mentor.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("first_name") == "HeadUpdated"


@pytest.mark.asyncio
async def test_update_mentor_self_as_mentor(mentor, mentor_client: AsyncClient):
    update_data = {"first_name": "SelfUpdated"}
    response = await mentor_client.patch(f"/api/v1/mentor/{mentor.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("first_name") == "SelfUpdated"


@pytest.mark.asyncio
async def test_update_other_mentor_as_mentor_forbidden(mentor_client: AsyncClient, other_mentor):
    update_data = {"first_name": "ShouldFail"}
    response = await mentor_client.patch(f"/api/v1/mentor/{other_mentor.id}", json=update_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_update_mentor_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    update_data = {"first_name": "Updated"}
    response = await superuser_client.patch(f"/api/v1/mentor/{non_existent_id}", json=update_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Mentor not found"


@pytest.mark.asyncio
async def test_update_mentor_unauthorized(unauthorized_client: AsyncClient):
    mentor_id = uuid4()
    update_data = {"first_name": "Updated"}
    response = await unauthorized_client.patch(f"/api/v1/mentor/{mentor_id}", json=update_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
