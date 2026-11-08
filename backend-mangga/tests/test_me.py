from fastapi.testclient import TestClient

from .conftest import auth_headers, login
from .test_inventory_rfq import register


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user_profile(client: TestClient) -> None:
    register(client, email="buyer@example.com", role="BUYER_B2B", name="Budi Santoso")
    token = login(client, "buyer@example.com", "testpass123")

    response = client.get("/api/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["namaLengkap"] == "Budi Santoso"
    assert body["email"] == "buyer@example.com"
    assert body["role"] == "BUYER_B2B"
    assert "hashedPassword" not in body and "password" not in body
