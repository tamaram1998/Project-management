from conftest import *
from conftest import status
import pytest
from unittest.mock import AsyncMock, Mock
from unittest import mock
from app.crud.documents import download_project_document


def test_download_document(
    mock_download_project_document, test_client_with_auth, test_project
):
    response = test_client_with_auth.get("/document/1")

    # Check response status code and content
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["Content-Disposition"] == "attachment; filename=document.pdf"
    )
    assert response.headers["Content-Type"] == "application/octet-stream"
    assert response.content == b"Test file content"


# Testing upload documents
@pytest.mark.asyncio
async def test_upload_documents(test_client_with_auth, test_project, s3_client):
    # Files to upload
    files = [
        ("files", ("testfile1.pdf", b"Content1", "text/plain")),
        ("files", ("testfile2.pdf", b"Content 2", "text/plain")),
    ]
    response = test_client_with_auth.post("/project/1/documents/", files=files)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Files uploaded successfully"}


# Testing to get list of all project documents
@pytest.mark.asyncio
async def test_list_all_project_documents(
    test_client_with_auth, test_project, bucket_name, s3_client, mocker
):
    response = test_client_with_auth.get("/project/1/documents")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": 1, "filename": "document.pdf"}]


# Testing deleting the documents
@pytest.mark.asyncio
async def test_delete_document(
    test_client_with_auth, test_project, bucket_name, s3_client, mocker
):
    response = test_client_with_auth.delete("/document/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert response.headers.get("application/json") is None
