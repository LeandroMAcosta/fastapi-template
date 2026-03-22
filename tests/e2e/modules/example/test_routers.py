"""E2E tests — hit real endpoints with a real database (testcontainers)."""

from uuid import uuid4

from app.core.auth import create_access_token


def get_auth_header():
    token = create_access_token(user_id=uuid4())
    return {"Authorization": f"Bearer {token}"}


class TestExampleCreate:
    def test_returns_201(self, client):
        response = client.post(
            "/api/v1/examples",
            json={"name": "Test Example", "description": "A test description"},
            headers=get_auth_header(),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Example"
        assert data["description"] == "A test description"
        assert data["id"] is not None
        assert data["created_by_id"] is not None

    def test_without_description(self, client):
        response = client.post(
            "/api/v1/examples",
            json={"name": "No Description"},
            headers=get_auth_header(),
        )
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_without_auth_returns_403(self, client):
        response = client.post("/api/v1/examples", json={"name": "Test"})
        assert response.status_code == 403

    def test_missing_name_returns_422(self, client):
        response = client.post(
            "/api/v1/examples",
            json={"description": "Missing name"},
            headers=get_auth_header(),
        )
        assert response.status_code == 422


class TestExampleList:
    def test_returns_paginated(self, client):
        response = client.get("/api/v1/examples", headers=get_auth_header())
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_with_name_filter(self, client):
        client.post(
            "/api/v1/examples",
            json={"name": "Filterable Item"},
            headers=get_auth_header(),
        )
        response = client.get(
            "/api/v1/examples?name__ilike=%25Filterable%25",
            headers=get_auth_header(),
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert any("Filterable" in item["name"] for item in items)


class TestExampleGetById:
    def test_get_existing(self, client):
        headers = get_auth_header()
        create_response = client.post(
            "/api/v1/examples",
            json={"name": "Get Me"},
            headers=headers,
        )
        example_id = create_response.json()["id"]

        response = client.get(f"/api/v1/examples/{example_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Get Me"

    def test_not_found(self, client):
        response = client.get(f"/api/v1/examples/{uuid4()}", headers=get_auth_header())
        assert response.status_code == 404


class TestExampleUpdate:
    def test_update_name(self, client):
        headers = get_auth_header()
        create_response = client.post(
            "/api/v1/examples", json={"name": "Original"}, headers=headers,
        )
        example_id = create_response.json()["id"]

        response = client.patch(
            f"/api/v1/examples/{example_id}", json={"name": "Updated"}, headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

    def test_partial_update_keeps_other_fields(self, client):
        headers = get_auth_header()
        create_response = client.post(
            "/api/v1/examples",
            json={"name": "Keep Me", "description": "Original Desc"},
            headers=headers,
        )
        example_id = create_response.json()["id"]

        response = client.patch(
            f"/api/v1/examples/{example_id}", json={"description": "New Desc"}, headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Keep Me"
        assert response.json()["description"] == "New Desc"


class TestExampleDelete:
    def test_returns_204_and_removes(self, client):
        headers = get_auth_header()
        create_response = client.post(
            "/api/v1/examples", json={"name": "Delete Me"}, headers=headers,
        )
        example_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/examples/{example_id}", headers=headers)
        assert response.status_code == 204

        get_response = client.get(f"/api/v1/examples/{example_id}", headers=headers)
        assert get_response.status_code == 404

    def test_not_found(self, client):
        response = client.delete(f"/api/v1/examples/{uuid4()}", headers=get_auth_header())
        assert response.status_code == 404


class TestHealthCheck:
    def test_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
