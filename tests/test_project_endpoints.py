from conftest import *
from sqlalchemy import text


def test_create_project(test_client_with_auth):
    response = test_client_with_auth.post(
        "/projects", json={"name": "New Project", "description": "New Description"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "New Description"
    assert "project_id" in data
    assert "owner_id" in data


#
def test_create_project_empty_name(test_client_with_auth):
    response = test_client_with_auth.post(
        "/projects", json={"name": "", "description": "New Description"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_projects(test_client_with_auth, test_project):
    response = test_client_with_auth.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_project_details(test_client_with_auth, test_project):
    response = test_client_with_auth.get("/project/1/info")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["owner_id"] is not None
    assert data["project_id"] == 1
    assert data["name"] == "Test Project"
    assert data["description"] == "Test Description"


def test_get_nonexistent_project_details(test_client_with_auth, test_project):
    response = test_client_with_auth.get("/project/999/info")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_update_project_details(test_client_with_auth, test_project):
    update_data = {"name": "Updated Project", "description": "Updated Description"}
    response = test_client_with_auth.put("/project/1/info", json=update_data)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "name": "Updated Project",
        "description": "Updated Description",
    }


def test_update_nonexistent_project(test_client_with_auth):
    update_data = {
        "name": "Nonexistent Project",
        "description": "Nonexistent Description",
    }
    response = test_client_with_auth.put("/project/999/info", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_delete_project(test_client_with_auth, test_project):
    response = test_client_with_auth.delete("/project/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_nonexistent_project(test_client_with_auth, test_project):
    response = test_client_with_auth.delete("/project/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}
