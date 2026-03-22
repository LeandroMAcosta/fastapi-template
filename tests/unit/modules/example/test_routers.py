from app.core.auth import create_access_token
from uuid import uuid4


def get_auth_header():
    token = create_access_token(user_id=uuid4())
    return {"Authorization": f"Bearer {token}"}


class TestExampleEndpoints:
    def test_create_example(self, client):
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

    def test_list_examples(self, client):
        response = client.get("/api/v1/examples", headers=get_auth_header())
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_example_not_found(self, client):
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/examples/{fake_id}", headers=get_auth_header())
        assert response.status_code == 404

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
