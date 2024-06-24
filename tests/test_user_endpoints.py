from conftest import *


# Test creating a new user
@pytest.mark.asyncio
async def test_create_user(test_client_with_auth):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "newuser@example.com",
            "password": "Testpassword!",
            "repeat_password": "Testpassword!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] is not None
    assert data["username"] == "newuser@example.com"
    assert data["hashed_password"] is not None


# Test creating a user with an existing username
def test_create_user_duplicate(test_client_with_auth, create_user):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "testuser@example.com",
            "password": "Testpassword!",
            "repeat_password": "Testpassword!",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "This username is already in use"}


# Test creating user with too short password
def test_create_user_password_too_short(test_client_with_auth):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "shortpassworduser@example.com",
            "password": "Short1!",
            "repeat_password": "Short1!",
        },
    )
    assert response.status_code == 422
    assert any(
        error["msg"] == "Value error, Password must be at least 10 characters long"
        for error in response.json()["detail"]
    )


# Test creating user with too long password
def test_create_user_password_too_long(test_client_with_auth):
    long_password = "A" * 100 + "a!"
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "longpassworduser@example.com",
            "password": long_password,
            "repeat_password": long_password,
        },
    )
    assert response.status_code == 422
    assert any(
        error["msg"] == "Value error, Password must be no more than 128 characters long"
        for error in response.json()["detail"]
    )


# Test creating user with missing uppercase password
def test_create_user_password_missing_uppercase(test_client_with_auth):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "noupperuser@example.com",
            "password": "nouppercase1!",
            "repeat_password": "nouppercase1!",
        },
    )
    assert response.status_code == 422
    assert any(
        error["msg"]
        == "Value error, Password must contain at least one uppercase letter"
        for error in response.json()["detail"]
    )


# Test creating user without special character
def test_create_user_password_without_special_character(test_client_with_auth):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "nospecialcharuser@example.com",
            "password": "Nospecialchar1",
            "repeat_password": "Nospecialchar1",
        },
    )
    assert response.status_code == 422
    assert any(
        error["msg"]
        == "Value error, Password must contain at least one special character"
        for error in response.json()["detail"]
    )


# Test creating user without matching passwords
def test_create_user_passwords_do_not_match(test_client_with_auth):
    response = test_client_with_auth.post(
        "/auth",
        json={
            "username": "nomatchuser@example.com",
            "password": "Validpassword123!",
            "repeat_password": "Differentpassword123!",
        },
    )
    assert response.status_code == 422
    assert any(
        error["msg"] == "Value error, Passwords don't match"
        for error in response.json()["detail"]
    )
