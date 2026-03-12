import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

from app.domain.entities.employee.enum import EmploymentStatus, EnglishLevel, InternshipStatus


@pytest.mark.asyncio
async def test_create_intern_as_superuser(superuser_client: AsyncClient, test_mentor_for_intern):
    intern_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "new_intern@example.com",
        "city": "Moscow",
        "unit_id": str(test_mentor_for_intern.unit_id),
        "mentor_id": str(test_mentor_for_intern.id),
        "status": InternshipStatus.awaited,
        "notes": "",
        "employment_status": EmploymentStatus.student,
        "university_name": "MSU",
        "english_level": EnglishLevel.A2,
    }
    response = await superuser_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("email") == "new_intern@example.com"
    assert json_data.get("first_name") == "John"
    assert json_data.get("last_name") == "Doe"
    assert json_data.get("mentor", {}).get("id") == str(test_mentor_for_intern.id)


@pytest.mark.asyncio
async def test_create_intern_as_head_mentor(head_mentor_client: AsyncClient, test_mentor_for_intern):
    intern_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "another_intern@example.com",
        "city": "Saint Petersburg",
        "unit_id": str(test_mentor_for_intern.unit_id),
        "mentor_id": str(test_mentor_for_intern.id),
        "english_level": EnglishLevel.A2,
    }
    response = await head_mentor_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("email") == "another_intern@example.com"


@pytest.mark.asyncio
async def test_create_intern_as_mentor_forbidden(mentor_client: AsyncClient, test_mentor_for_intern):
    intern_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "city": "Moscow",
        "unit_id": str(test_mentor_for_intern.unit_id),
        "mentor_id": str(test_mentor_for_intern.id),
        "english_level": EnglishLevel.A2,
    }
    response = await mentor_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_create_intern_with_archived_mentor(superuser_client: AsyncClient, archived_mentor_for_intern):
    intern_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "city": "Moscow",
        "unit_id": str(archived_mentor_for_intern.unit_id),
        "mentor_id": str(archived_mentor_for_intern.id),
        "english_level": EnglishLevel.A2,
    }
    response = await superuser_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json().get("detail") == "Mentor is archived"


@pytest.mark.asyncio
async def test_create_intern_head_mentor_different_unit_forbidden(
    head_mentor_client: AsyncClient, test_mentor_for_intern, another_unit
):
    """Head mentor cannot create intern with unit_id different from their own."""
    intern_data = {
        "first_name": "Other",
        "last_name": "Unit",
        "email": "other_unit_intern@example.com",
        "city": "Moscow",
        "unit_id": str(another_unit.id),
        "mentor_id": str(test_mentor_for_intern.id),
        "english_level": "A2",
    }
    response = await head_mentor_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_403_FORBIDDEN
    assert "unit" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_intern_unauthorized(unauthorized_client: AsyncClient, test_mentor_for_intern):
    intern_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "city": "Moscow",
        "unit_id": str(test_mentor_for_intern.unit_id),
        "mentor_id": str(test_mentor_for_intern.id),
        "english_level": EnglishLevel.A2,
    }
    response = await unauthorized_client.post("/api/v1/intern", json=intern_data)
    assert response.status_code == HTTP_401_UNAUTHORIZED
