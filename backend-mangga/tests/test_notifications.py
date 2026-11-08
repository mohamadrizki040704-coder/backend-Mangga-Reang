from fastapi.testclient import TestClient

from models.domain_models import User

from .conftest import auth_headers, login
from .test_inventory_rfq import create_inventory, register


def _notifs(client: TestClient, token: str) -> list[dict]:
    response = client.get("/api/notifikasi/", headers=auth_headers(token))
    assert response.status_code == 200, response.text
    return response.json()


def _make_rfq(client: TestClient) -> tuple[str, int]:
    register(client, email="farmer@example.com", role="PETANI", name="Farmer")
    inventory_id = create_inventory(client, login(client, "farmer@example.com", "testpass123"))
    register(client, email="buyer@example.com", role="BUYER_B2B", name="Buyer")
    buyer_token = login(client, "buyer@example.com", "testpass123")
    rfq_id = client.post(
        "/api/rfq/",
        headers=auth_headers(buyer_token),
        json={"idMangga": inventory_id, "tonaseDiminta": 2},
    ).json()["id"]
    return buyer_token, rfq_id


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/notifikasi/").status_code == 401
    assert client.put("/api/notifikasi/read-all").status_code == 401


def test_register_creates_welcome_notification(client: TestClient) -> None:
    register(client, email="buyer@example.com", role="BUYER_B2B", name="Buyer")
    items = _notifs(client, login(client, "buyer@example.com", "testpass123"))

    assert len(items) == 1
    assert items[0]["title"].startswith("Selamat datang")
    assert items[0]["read"] is False
    assert {"id", "title", "message", "createdAt", "read"} <= set(items[0])


def test_rfq_flow_notifies_buyer_and_admin(client: TestClient, admin_user: User) -> None:
    buyer_token, rfq_id = _make_rfq(client)
    admin_token = login(client, "admin@example.com", "adminpass123")

    admin_items = _notifs(client, admin_token)
    assert any(f"#{rfq_id}" in i["message"] for i in admin_items)

    buyer_titles = [i["title"] for i in _notifs(client, buyer_token)]
    assert "Permintaan penawaran terkirim" in buyer_titles

    assert client.put(
        f"/api/rfq/{rfq_id}/approve", headers=auth_headers(admin_token)
    ).status_code == 200
    buyer_titles = [i["title"] for i in _notifs(client, buyer_token)]
    assert "Penawaran disetujui" in buyer_titles

    response = client.post(
        f"/api/logistik/{rfq_id}/update-status",
        headers=auth_headers(admin_token),
        json={"statusMilestone": "IN_TRANSIT"},
    )
    assert response.status_code == 201, response.text
    latest = _notifs(client, buyer_token)[0]
    assert latest["title"] == "Status pengiriman diperbarui"
    assert "pengiriman" in latest["message"]


def test_unread_count_and_mark_read(client: TestClient) -> None:
    register(client, email="buyer@example.com", role="BUYER_B2B", name="Buyer")
    token = login(client, "buyer@example.com", "testpass123")

    count = client.get("/api/notifikasi/unread-count", headers=auth_headers(token))
    assert count.json() == {"count": 1}

    note_id = _notifs(client, token)[0]["id"]
    one = client.put(f"/api/notifikasi/{note_id}/read", headers=auth_headers(token))
    assert one.status_code == 200 and one.json()["read"] is True
    assert client.get("/api/notifikasi/unread-count", headers=auth_headers(token)).json() == {
        "count": 0
    }


def test_mark_all_read(client: TestClient, admin_user: User) -> None:
    buyer_token, _ = _make_rfq(client)
    response = client.put("/api/notifikasi/read-all", headers=auth_headers(buyer_token))
    assert response.status_code == 200
    assert response.json()["updated"] >= 2
    assert all(i["read"] for i in _notifs(client, buyer_token))
    assert client.get(
        "/api/notifikasi/?unread_only=true", headers=auth_headers(buyer_token)
    ).json() == []


def test_users_cannot_touch_each_others_notifications(client: TestClient) -> None:
    register(client, email="a@example.com", role="BUYER_B2B", name="A")
    register(client, email="b@example.com", role="BUYER_B2B", name="B")
    token_a = login(client, "a@example.com", "testpass123")
    token_b = login(client, "b@example.com", "testpass123")

    a_note_id = _notifs(client, token_a)[0]["id"]
    response = client.put(f"/api/notifikasi/{a_note_id}/read", headers=auth_headers(token_b))
    assert response.status_code == 404
    assert _notifs(client, token_a)[0]["read"] is False
