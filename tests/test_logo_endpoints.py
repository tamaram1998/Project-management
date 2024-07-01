from conftest import *
from conftest import status
import pytest
from unittest.mock import AsyncMock, Mock

from app.crud.logo import (
    upload_to_s3,
    allowed_file_extension,
    get_project_logo_url,
    download_logo_from_s3,
    delete_logo,
)


# Test uploading a logo
@pytest.mark.asyncio
async def test_upload_project_logo(
    test_client_with_auth, test_project, s3_client, mocker
):
    mocker.patch(
        "app.crud.logo.upload_to_s3",
        new=AsyncMock(return_value={"logo_url": "http://example.com/logo.png"}),
    )
    mocker.patch("app.crud.logo.allowed_file_extension", return_value=True)

    files = {
        "file": ("logo.png", b"file_content", "image/png"),
    }
    response = test_client_with_auth.put("/project/1/logo", files=files)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Logo uploaded successfully"}


# Test uploading a logo with invalid file extension
@pytest.mark.asyncio
async def test_upload_project_logo_invalid_extension(
    test_client_with_auth, test_project, s3_client, mocker
):
    mocker.patch("app.crud.logo.allowed_file_extension", return_value=False)

    files = {
        "file": ("logo.txt", b"file_content", "text/plain"),
    }
    response = test_client_with_auth.put("/project/1/logo", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Only .jpg, .jpeg, and .png files are allowed"}


# Test downloading a logo
@pytest.mark.asyncio
async def test_download_project_logo(
    test_client_with_auth, test_project, s3_client, mocker
):
    mocker.patch(
        "app.crud.logo.get_project_logo_url", return_value="http://example.com/logo.png"
    )
    mocker.patch(
        "app.crud.logo.download_logo_from_s3", return_value=(b"file_content", None)
    )

    response = test_client_with_auth.get("/project/1/logo")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Disposition"] == "attachment; filename=logo.png"
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert response.content == b"file_content"


# Test deleting a logo
@pytest.mark.asyncio
async def test_delete_project_logo(
    test_client_with_auth, test_project, s3_client, mocker
):
    mocker.patch("app.crud.logo.delete_logo", new=AsyncMock(return_value=None))

    response = test_client_with_auth.delete("/project/1/logo")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
