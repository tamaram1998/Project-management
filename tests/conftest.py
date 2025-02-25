import pytest
import os
import boto3
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from fastapi import status
from unittest.mock import Mock

from app.main import app, get_db
from app.models import Project, User, Document, ProjectParticipant
from app.auth.jwt_handler import SECRET_KEY, hash_pass, ALGORITHM
from datetime import datetime, timedelta
from moto import mock_aws
from jose import JWTError, jwt

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
engine = create_engine(TEST_DATABASE_URL)

# Configured session class
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def mock_download_project_document(mocker):
    mock_download_function = mocker.patch(
        "app.crud.documents.download_project_document", new_callable=Mock
    )
    mock_download_function.return_value = (b"Test file content", None)
    return mock_download_function


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@pytest.fixture(scope="function")
def create_user(db_session):
    email = "testuser@example.com"
    try:
        existing_user = db_session.query(User).filter_by(email=email).one()
        return existing_user
    except NoResultFound:
        # User does not exist, create new user
        new_user = User(email=email, hashed_password="testpassword")
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        return new_user


@pytest.fixture(scope="function")
def token(create_user):
    test_user = create_user.__dict__
    token = create_access_token(data={"sub": test_user["email"]})
    return token


@pytest.fixture(scope="function")
def test_client_with_auth(db_session, token):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    headers = {"Authorization": f"Bearer {token}"}
    with TestClient(app, headers=headers) as client:
        yield client


@pytest.fixture
def s3_client():
    with mock_aws():
        conn = boto3.client(
            "s3",
            region_name="us-east-1",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        yield conn


@pytest.fixture
def bucket_name():
    return "my-test-bucket"


# Clear the content of specific tables before each test
@pytest.fixture(scope="function", autouse=True)
def setup(db_session):
    db_session.execute(text("TRUNCATE TABLE projects RESTART IDENTITY CASCADE"))
    db_session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    db_session.commit()


# Create a new database session with a rollback at the end of the test
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    # transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    # transaction.rollback()
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


# Fixture to create a test project in the database
@pytest.fixture()
def test_project(db_session, create_user):
    owner_user = create_user
    db_session.add(owner_user)
    db_session.commit()

    # Create project and assign owner
    new_project = Project(
        name="Test Project",
        description="Test Description",
        owner_id=owner_user.id,
        logo_url="https://example.com/logo.png",
    )
    db_session.add(new_project)

    # Create participant user if not exists
    email = "Participant User"
    participant_user = db_session.query(User).filter_by(email=email).first()
    if not participant_user:
        participant_user = User(email=email, hashed_password="12345")
        db_session.add(participant_user)

    if participant_user not in new_project.participants:
        new_project.participants.append(participant_user)
        db_session.commit()

    # Adding a document to the project
    new_document = Document(
        filename="document.pdf",
        file_url="http://example.com/document.pdf",
        project=new_project,
    )

    db_session.add(new_document)
    db_session.commit()

    return new_project
