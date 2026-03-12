import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_units_as_superuser(superuser_client: AsyncClient, default_unit, another_unit):
    """Superuser can list all units."""
    response = await superuser_client.get("/api/v1/unit")
    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    ids = [u["id"] for u in data]
    names = [u["name"] for u in data]
    assert str(default_unit.id) in ids
    assert str(another_unit.id) in ids
    assert "Default" in names
    assert "Other Unit" in names


@pytest.mark.asyncio
async def test_get_units_as_head_mentor_forbidden(head_mentor_client: AsyncClient):
    """Head mentor cannot list units (only superuser)."""
    response = await head_mentor_client.get("/api/v1/unit")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_get_units_as_mentor_forbidden(mentor_client: AsyncClient):
    """Mentor cannot list units (only superuser)."""
    response = await mentor_client.get("/api/v1/unit")
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_get_units_unauthorized(unauthorized_client: AsyncClient):
    """Unauthenticated user cannot list units."""
    response = await unauthorized_client.get("/api/v1/unit")
    assert response.status_code == HTTP_401_UNAUTHORIZED
