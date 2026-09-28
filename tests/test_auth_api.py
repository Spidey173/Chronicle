"""API tests for authentication and role authorization."""

from fastapi import status


def test_register_user_success(client):
    payload = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "Password123!",
        "role": "user"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "Dup User",
        "password": "Password123!",
        "role": "user"
    }
    resp1 = client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == status.HTTP_201_CREATED

    resp2 = client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in resp2.json()["detail"]


def test_login_success(client, normal_user):
    payload = {
        "email": normal_user.email,
        "password": "UserPass123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == normal_user.email


def test_login_invalid_password(client, normal_user):
    payload = {
        "email": normal_user.email,
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_authorized(client, user_token_headers):
    response = client.get("/api/v1/auth/me", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test_user@example.com"


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
