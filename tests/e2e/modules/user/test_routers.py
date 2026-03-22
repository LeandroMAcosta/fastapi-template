"""E2E tests for user endpoints — real DB via testcontainers."""

from uuid import uuid4

from tests.factories.user import RegisterRequestFactory


def register_and_get_token(client) -> tuple[str, dict]:
    """Helper: register a user and return (token, user_data)."""
    data = RegisterRequestFactory.build()
    register_response = client.post("/api/v1/auth/register", json=data.model_dump())
    user_data = register_response.json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": data.email, "password": data.password},
    )
    token = login_response.json()["access_token"]
    return token, user_data


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestGetMe:
    def test_returns_current_user(self, client):
        token, user_data = register_and_get_token(client)

        response = client.get("/api/v1/users/me", headers=auth_header(token))
        assert response.status_code == 200
        assert response.json()["id"] == user_data["id"]
        assert response.json()["email"] == user_data["email"]

    def test_without_auth_returns_403(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code == 403


class TestListUsers:
    def test_returns_paginated(self, client):
        token, _ = register_and_get_token(client)

        response = client.get("/api/v1/users", headers=auth_header(token))
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body
        assert body["total"] >= 1


class TestGetUser:
    def test_get_existing_user(self, client):
        token, user_data = register_and_get_token(client)

        response = client.get(f"/api/v1/users/{user_data['id']}", headers=auth_header(token))
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]

    def test_get_nonexistent_returns_404(self, client):
        token, _ = register_and_get_token(client)

        response = client.get(f"/api/v1/users/{uuid4()}", headers=auth_header(token))
        assert response.status_code == 404


class TestUpdateUser:
    def test_update_first_name(self, client):
        token, user_data = register_and_get_token(client)

        response = client.patch(
            f"/api/v1/users/{user_data['id']}",
            json={"first_name": "Updated"},
            headers=auth_header(token),
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"
        assert response.json()["last_name"] == user_data["last_name"]
