"""E2E tests for user endpoints — real DB via testcontainers."""

from datetime import UTC
from uuid import uuid4

from httpx import AsyncClient

from tests.factories.user import RegisterRequestFactory


async def register_and_get_token(client: AsyncClient) -> tuple[str, dict]:
    """Helper: register a user and return (token, user_data)."""
    data = RegisterRequestFactory.build()
    register_response = await client.post("/api/v1/auth/register", json=data.model_dump())
    user_data = register_response.json()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": data.email, "password": data.password},
    )
    token = login_response.json()["access_token"]
    return token, user_data


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestGetMe:
    async def test_returns_current_user(self, client):
        token, user_data = await register_and_get_token(client)

        response = await client.get("/api/v1/users/me", headers=auth_header(token))
        assert response.status_code == 200
        assert response.json()["id"] == user_data["id"]
        assert response.json()["email"] == user_data["email"]

    async def test_without_auth_returns_403(self, client):
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 403

    async def test_with_invalid_token_returns_401(self, client):
        response = await client.get("/api/v1/users/me", headers=auth_header("invalid-token"))
        assert response.status_code == 401

    async def test_with_expired_token_returns_401(self, client):
        from datetime import datetime, timedelta

        import jwt

        from app.core.config import settings

        expired_token = jwt.encode(
            {
                "sub": str(uuid4()),
                "type": "access",
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "iat": datetime.now(UTC) - timedelta(hours=2),
            },
            settings.AUTH_JWT_SECRET,
            algorithm=settings.AUTH_JWT_ALGORITHM,
        )
        response = await client.get("/api/v1/users/me", headers=auth_header(expired_token))
        assert response.status_code == 401

    async def test_with_refresh_token_returns_401(self, client):
        """Refresh tokens should not be accepted as access tokens."""
        token, _ = await register_and_get_token(client)
        # Get a refresh token
        data = RegisterRequestFactory.build()
        await client.post("/api/v1/auth/register", json=data.model_dump())
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": data.email, "password": data.password},
        )
        refresh_token = login_resp.json()["refresh_token"]

        response = await client.get("/api/v1/users/me", headers=auth_header(refresh_token))
        assert response.status_code == 401


class TestListUsers:
    async def test_returns_paginated(self, client):
        token, _ = await register_and_get_token(client)

        response = await client.get("/api/v1/users", headers=auth_header(token))
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body
        assert body["total"] >= 1


class TestGetUser:
    async def test_get_existing_user(self, client):
        token, user_data = await register_and_get_token(client)

        response = await client.get(f"/api/v1/users/{user_data['id']}", headers=auth_header(token))
        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]

    async def test_get_nonexistent_returns_404(self, client):
        token, _ = await register_and_get_token(client)

        response = await client.get(f"/api/v1/users/{uuid4()}", headers=auth_header(token))
        assert response.status_code == 404


class TestUpdateUser:
    async def test_update_first_name(self, client):
        token, user_data = await register_and_get_token(client)

        response = await client.patch(
            f"/api/v1/users/{user_data['id']}",
            json={"first_name": "Updated"},
            headers=auth_header(token),
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "Updated"
        assert response.json()["last_name"] == user_data["last_name"]
