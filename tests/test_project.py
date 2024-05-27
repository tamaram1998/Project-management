import pytest
from fastapi.testclient import TestClient
from fastapi import status
from src.main import app, projects_db, Project

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    projects_db.clear()
    projects_db[1] = Project(id=1, name="Test Project", description="Test Description")
    yield
    projects_db.clear()


def test_create_project():
    project = {"name": "New Project", "description": "New Description"}
    response = client.post("/projects", json=project)
    assert response.status_code == status.HTTP_201_CREATED
    response_json_data = response.json()
    assert response.json() == {"id": 2, "name": "New Project", "description": "New Description"}

def test_create_project_empty_name():
    project = {"name": "", "description": "New Description"}
    response = client.post("/projects", json=project)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_projects():
    response = client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_project_details():
    response = client.get("/project/1/info")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": 1, "name": "Test Project", "description": "Test Description"}


def test_get_nonexistent_project_details():
    response = client.get("/project/999/info")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_update_project_details():
    update_data = {"name": "Updated Project", "description": "Updated Description"}
    response = client.put("/project/1/info", json=update_data)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"id": 1, "name": "Updated Project", "description": "Updated Description"}


def test_update_nonexistent_project():
    update_data = {"name": "Nonexistent Project", "description": "Nonexistent Description"}
    response = client.put("/project/999/info", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_delete_project():
    response = client.delete("/project/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_nonexistent_project():
    response = client.delete("/project/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}
