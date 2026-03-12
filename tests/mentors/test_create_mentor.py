import pytest
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.domain.entities.employee.enum import Role


@pytest.mark.asyncio
async def test_create_mentor_as_superuser(superuser_client: AsyncClient, default_unit):
    mentor_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "new_mentor@example.com",
        "city": "Moscow",
        "unit_id": str(default_unit.id),
        "available": True,
        "available_for_interview": True,
    }
    response = await superuser_client.post("/api/v1/mentor", json=mentor_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("email") == "new_mentor@example.com"
    assert json_data.get("first_name") == "John"
    assert json_data.get("last_name") == "Doe"
    assert json_data.get("role") == Role.mentor


@pytest.mark.asyncio
async def test_create_mentor_as_head_mentor(head_mentor_client: AsyncClient, default_unit):
    mentor_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "another_mentor@example.com",
        "city": "Saint Petersburg",
        "unit_id": str(default_unit.id),
        "available": True,
        "available_for_interview": True,
    }
    response = await head_mentor_client.post("/api/v1/mentor", json=mentor_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("email") == "another_mentor@example.com"


@pytest.mark.asyncio
async def test_create_mentor_as_mentor_forbidden(mentor_client: AsyncClient, default_unit):
    mentor_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "city": "Moscow",
        "unit_id": str(default_unit.id),
        "available": True,
        "available_for_interview": True,
    }
    response = await mentor_client.post("/api/v1/mentor", json=mentor_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_create_mentor_head_mentor_different_unit_forbidden(head_mentor_client: AsyncClient, another_unit):
    """Head mentor cannot create mentor in a unit different from their own."""
    mentor_data = {
        "first_name": "Other",
        "last_name": "Unit",
        "email": "other_unit_mentor@example.com",
        "city": "Moscow",
        "unit_id": str(another_unit.id),
        "available": True,
        "available_for_interview": True,
    }
    response = await head_mentor_client.post("/api/v1/mentor", json=mentor_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert "unit" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_mentor_unauthorized(unauthorized_client: AsyncClient, default_unit):
    mentor_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "city": "Moscow",
        "unit_id": str(default_unit.id),
    }
    response = await unauthorized_client.post("/api/v1/mentor", json=mentor_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
