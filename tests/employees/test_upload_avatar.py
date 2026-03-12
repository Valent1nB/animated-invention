from io import BytesIO
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)


@pytest.mark.asyncio
async def test_upload_avatar_for_mentor_as_superuser(superuser_client: AsyncClient, test_mentor_for_avatar):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await superuser_client.post(
        f"/api/v1/employee/{test_mentor_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("id") == str(test_mentor_for_avatar.id)
    assert json_data.get("avatar_key") is not None
    assert json_data.get("avatar_key") != ""


@pytest.mark.asyncio
async def test_upload_avatar_for_mentor_as_head_mentor(head_mentor_client: AsyncClient, test_mentor_for_avatar):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.jpg", file_content, "image/jpeg")}
    response = await head_mentor_client.post(
        f"/api/v1/employee/{test_mentor_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("avatar_key") is not None


@pytest.mark.asyncio
async def test_upload_avatar_for_self_as_mentor(mentor, mentor_client: AsyncClient):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await mentor_client.post(
        f"/api/v1/employee/{mentor.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("id") == str(mentor.id)
    assert json_data.get("avatar_key") is not None


@pytest.mark.asyncio
async def test_upload_avatar_for_intern_as_superuser(superuser_client: AsyncClient, test_intern_for_avatar):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await superuser_client.post(
        f"/api/v1/employee/{test_intern_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("id") == str(test_intern_for_avatar.id)
    assert json_data.get("avatar_key") is not None


@pytest.mark.asyncio
async def test_upload_avatar_for_own_intern_as_mentor_via_fixture(
    mentor, mentor_client: AsyncClient, intern_for_logged_in_mentor
):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await mentor_client.post(
        f"/api/v1/employee/{intern_for_logged_in_mentor.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_201_CREATED

    json_data = response.json()
    assert json_data.get("id") == str(intern_for_logged_in_mentor.id)
    assert json_data.get("avatar_key") is not None


@pytest.mark.asyncio
async def test_upload_avatar_for_other_mentor_as_mentor_forbidden(mentor_client: AsyncClient, other_mentor_for_avatar):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await mentor_client.post(
        f"/api/v1/employee/{other_mentor_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_upload_avatar_for_other_intern_as_mentor_forbidden(mentor_client: AsyncClient, intern_with_other_mentor):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await mentor_client.post(
        f"/api/v1/employee/{intern_with_other_mentor.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_403_FORBIDDEN
    assert response.json().get("detail") == "Access denied"


@pytest.mark.asyncio
async def test_upload_avatar_employee_not_found(superuser_client: AsyncClient):
    non_existent_id = uuid4()
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await superuser_client.post(
        f"/api/v1/employee/{non_existent_id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Employee not found"


@pytest.mark.asyncio
async def test_upload_avatar_unauthorized(unauthorized_client: AsyncClient):
    employee_id = uuid4()
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar.png", file_content, "image/png")}
    response = await unauthorized_client.post(
        f"/api/v1/employee/{employee_id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_upload_avatar_invalid_file_format(superuser_client: AsyncClient, test_mentor_for_avatar):
    file_content = BytesIO(b"fake file content")
    files = {"image": ("document.txt", file_content, "text/plain")}
    response = await superuser_client.post(
        f"/api/v1/employee/{test_mentor_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_avatar_no_file_extension(superuser_client: AsyncClient, test_mentor_for_avatar):
    file_content = BytesIO(b"fake image content")
    files = {"image": ("avatar", file_content, "image/png")}
    response = await superuser_client.post(
        f"/api/v1/employee/{test_mentor_for_avatar.id}/upload-avatar",
        files=files,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
