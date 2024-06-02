import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi import status
from src.main import app, get_db
from src.models import Project

DATABASE_URL = "postgresql://postgres@localhost/test_db"
engine = create_engine(DATABASE_URL)

# configured session class
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup(db_session):
    """Setup: clear the content of specific tables before each test."""
    db_session.execute(text("TRUNCATE TABLE projects RESTART IDENTITY CASCADE"))
    db_session.commit()


# Create a new database session with a rollback at the end of the test.
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# Create a test client that uses the override_get_db
@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# Fixture to create a test project in the database.
@pytest.fixture
def test_project(db_session):
    new_project = Project(name="Test Project", description="Test Description")
    db_session.add(new_project)
    db_session.commit()
    db_session.refresh(new_project)
    return new_project


def test_create_project(test_client):
    response = test_client.post(
        "/projects", json={"name": "New Project", "description": "New Description"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "New Description"
    assert "project_id" in data


def test_create_project_empty_name(test_client):
    response = test_client.post(
        "/projects", json={"name": "", "description": "New Description"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_projects(test_client, test_project):
    response = test_client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_project_details(test_client, test_project):
    response = test_client.get("/project/1/info")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "project_id": 1,
        "name": "Test Project",
        "description": "Test Description",
    }


def test_get_nonexistent_project_details(test_client, test_project):
    response = test_client.get("/project/999/info")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_update_project_details(test_client, test_project):
    update_data = {"name": "Updated Project", "description": "Updated Description"}
    response = test_client.put("/project/1/info", json=update_data)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
        "project_id": 1,
        "name": "Updated Project",
        "description": "Updated Description",
    }


def test_update_nonexistent_project(test_client):
    update_data = {
        "name": "Nonexistent Project",
        "description": "Nonexistent Description",
    }
    response = test_client.put("/project/999/info", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}


def test_delete_project(test_client, test_project):
    response = test_client.delete("/project/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_nonexistent_project(test_client, test_project):
    response = test_client.delete("/project/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Project with ID 999 not found"}
