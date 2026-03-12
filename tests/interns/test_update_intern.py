from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from app.domain.entities.employee.enum import InternshipStatus


@pytest.mark.asyncio
async def test_update_intern_as_superuser(superuser_client: AsyncClient, test_intern):
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "city": "New City",
        "status": InternshipStatus.active,
    }
    response = await superuser_client.patch(f"/api/v1/intern/{test_intern.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("first_name") == "Updated"
    assert json_data.get("last_name") == "Name"
    assert json_data.get("city") == "New City"
    assert json_data.get("status") == InternshipStatus.active


@pytest.mark.asyncio
async def test_update_intern_as_head_mentor(head_mentor_client: AsyncClient, test_intern):
    update_data = {"first_name": "HeadUpdated", "notes": "Updated notes"}
    response = await head_mentor_client.patch(f"/api/v1/intern/{test_intern.id}", json=update_data)
    assert response.status_code == HTTP_200_OK

    json_data = response.json()
    assert json_data.get("first_name") == "HeadUpdated"
    assert json_data.get("notes") == "Updated notes"


@pytest.mark.asyncio
async def test_update_intern_as_mentor_forbidden(mentor_client: AsyncClient, test_intern):
    update_data = {"first_name": "ShouldFail"}
    response = await mentor_client.patch(f"/api/v1/intern/{test_intern.id}", json=update_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_update_intern_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    update_data = {"first_name": "Updated"}
    response = await superuser_client.patch(f"/api/v1/intern/{non_existent_id}", json=update_data)
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Intern not found"


@pytest.mark.asyncio
async def test_update_intern_unauthorized(unauthorized_client: AsyncClient):
    intern_id = uuid4()
    update_data = {"first_name": "Updated"}
    response = await unauthorized_client.patch(f"/api/v1/intern/{intern_id}", json=update_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_intern_cannot_change_mentor(superuser_client: AsyncClient, test_intern, other_mentor_for_intern):
    update_data = {
        "mentor_id": str(other_mentor_for_intern.id),
    }
    response = await superuser_client.patch(f"/api/v1/intern/{test_intern.id}", json=update_data)
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
