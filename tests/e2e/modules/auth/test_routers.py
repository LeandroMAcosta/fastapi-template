"""E2E tests for auth endpoints — real DB via testcontainers."""

from tests.factories.user import RegisterRequestFactory


class TestRegister:
    def test_returns_201(self, client):
        data = RegisterRequestFactory.build()
        response = client.post("/api/v1/auth/register", json=data.model_dump())
        assert response.status_code == 201
        body = response.json()
        assert body["email"] == data.email
        assert body["first_name"] == data.first_name
        assert "hashed_password" not in body
        assert "id" in body

    def test_duplicate_email_returns_409(self, client):
        data = RegisterRequestFactory.build()
        client.post("/api/v1/auth/register", json=data.model_dump())

        response = client.post("/api/v1/auth/register", json=data.model_dump())
        assert response.status_code == 409


class TestLogin:
    def test_valid_credentials(self, client):
        data = RegisterRequestFactory.build()
        client.post("/api/v1/auth/register", json=data.model_dump())

        response = client.post(
            "/api/v1/auth/login",
            json={"email": data.email, "password": data.password},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_wrong_password(self, client):
        data = RegisterRequestFactory.build()
        client.post("/api/v1/auth/register", json=data.model_dump())

        response = client.post(
            "/api/v1/auth/login",
            json={"email": data.email, "password": "wrong-password"},
        )
        assert response.status_code == 401

    def test_nonexistent_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "pass"},
        )
        assert response.status_code == 401
