"""Tests for the GYDClient using mocked HTTP responses."""

from pathlib import Path

import pytest
import responses

from gather_your_deals.client import GYDClient
from gather_your_deals.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)

BASE = "http://localhost:8080/api/v1"


@pytest.fixture
def client(tmp_path: Path) -> GYDClient:
    """Create a client with a temporary config path and no persisted tokens."""
    return GYDClient(BASE, config_path=tmp_path / "env.yaml", auto_persist_tokens=False)


@pytest.fixture
def authed_client(tmp_path: Path) -> GYDClient:
    """Create a client pre-loaded with tokens."""
    c = GYDClient(BASE, config_path=tmp_path / "env.yaml", auto_persist_tokens=False)
    c.set_tokens("test-access", "test-refresh")
    return c


# ── Auth ─────────────────────────────────────────────────────────────────


class TestLogin:
    @responses.activate
    def test_login_success(self, client: GYDClient):
        responses.post(
            f"{BASE}/auth/login",
            json={
                "access_token": "at-1",
                "refresh_token": "rt-1",
                "token_type": "Bearer",
            },
        )
        tokens = client.login("alice", "password123")
        assert tokens.access_token == "at-1"
        assert tokens.refresh_token == "rt-1"
        assert client.is_authenticated

    @responses.activate
    def test_login_bad_credentials(self, client: GYDClient):
        responses.post(
            f"{BASE}/auth/login",
            json={"error": "invalid username or password"},
            status=401,
        )
        with pytest.raises(AuthenticationError):
            client.login("alice", "wrong")


class TestLogout:
    @responses.activate
    def test_logout(self, authed_client: GYDClient):
        responses.post(f"{BASE}/auth/logout", json={"message": "logged out"})
        result = authed_client.logout()
        assert result["message"] == "logged out"
        assert not authed_client.is_authenticated


class TestMe:
    @responses.activate
    def test_me(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/auth/me",
            json={"id": "u-1", "role": "user"},
        )
        info = authed_client.me()
        assert info["id"] == "u-1"
        assert info["role"] == "user"


# ── Users ────────────────────────────────────────────────────────────────


class TestRegister:
    @responses.activate
    def test_register_success(self, client: GYDClient):
        responses.post(
            f"{BASE}/users",
            json={"id": "u-new", "username": "bob", "role": "user"},
            status=201,
        )
        user = client.users.register("bob", "password123")
        assert user.username == "bob"
        assert user.role == "user"

    @responses.activate
    def test_register_conflict(self, client: GYDClient):
        responses.post(
            f"{BASE}/users",
            json={"error": "username already exists"},
            status=409,
        )
        with pytest.raises(ConflictError):
            client.users.register("alice", "password123")


# ── Meta ─────────────────────────────────────────────────────────────────


class TestMeta:
    @responses.activate
    def test_list_fields(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/meta",
            json=[
                {
                    "fieldName": "productName",
                    "description": "name of product",
                    "type": "string",
                    "native": True,
                },
                {
                    "fieldName": "brand",
                    "description": "brand of the product",
                    "type": "string",
                    "native": False,
                },
            ],
        )
        fields = authed_client.meta.list()
        assert len(fields) == 2
        assert fields[0].field_name == "productName"
        assert fields[0].native is True
        assert fields[1].field_name == "brand"

    @responses.activate
    def test_register_field(self, authed_client: GYDClient):
        responses.post(
            f"{BASE}/meta",
            json={
                "fieldName": "brand",
                "description": "brand of the product",
                "type": "string",
                "native": False,
            },
            status=201,
        )
        f = authed_client.meta.register("brand", "brand of the product", "string")
        assert f.field_name == "brand"

    @responses.activate
    def test_register_field_conflict(self, authed_client: GYDClient):
        responses.post(
            f"{BASE}/meta",
            json={"error": "field already exists"},
            status=409,
        )
        with pytest.raises(ConflictError):
            authed_client.meta.register("brand", "brand of the product", "string")


# ── Receipts ─────────────────────────────────────────────────────────────

SAMPLE_RECEIPT = {
    "id": "r-123",
    "productName": "Milk 2%",
    "purchaseDate": "2025.04.05",
    "price": "5.49CAD",
    "amount": "2lb",
    "storeName": "Costco",
    "latitude": 49.28,
    "longitude": -123.12,
    "uploadTime": 1770620311,
    "userId": "u-1",
}


class TestReceipts:
    @responses.activate
    def test_create_receipt(self, authed_client: GYDClient):
        responses.post(f"{BASE}/receipts", json=SAMPLE_RECEIPT, status=201)
        r = authed_client.receipts.create(
            product_name="Milk 2%",
            purchase_date="2025.04.05",
            price="5.49CAD",
            amount="2lb",
            store_name="Costco",
            latitude=49.28,
            longitude=-123.12,
        )
        assert r.id == "r-123"
        assert r.product_name == "Milk 2%"

    @responses.activate
    def test_create_with_extras(self, authed_client: GYDClient):
        resp = {**SAMPLE_RECEIPT, "brand": "Kirkland"}
        responses.post(f"{BASE}/receipts", json=resp, status=201)
        r = authed_client.receipts.create(
            product_name="Milk 2%",
            purchase_date="2025.04.05",
            price="5.49CAD",
            amount="2lb",
            store_name="Costco",
            extras={"brand": "Kirkland"},
        )
        assert r.extras["brand"] == "Kirkland"

    @responses.activate
    def test_list_receipts(self, authed_client: GYDClient):
        responses.get(f"{BASE}/receipts", json=[SAMPLE_RECEIPT])
        items = authed_client.receipts.list()
        assert len(items) == 1
        assert items[0].product_name == "Milk 2%"

    @responses.activate
    def test_get_receipt(self, authed_client: GYDClient):
        responses.get(f"{BASE}/receipts/r-123", json=SAMPLE_RECEIPT)
        r = authed_client.receipts.get("r-123")
        assert r.id == "r-123"

    @responses.activate
    def test_get_receipt_not_found(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/receipts/r-bad",
            json={"error": "receipt not found"},
            status=404,
        )
        with pytest.raises(NotFoundError):
            authed_client.receipts.get("r-bad")

    @responses.activate
    def test_delete_receipt(self, authed_client: GYDClient):
        responses.delete(
            f"{BASE}/receipts/r-123", json={"message": "receipt deleted"}
        )
        result = authed_client.receipts.delete("r-123")
        assert result["message"] == "receipt deleted"


# ── Admin ────────────────────────────────────────────────────────────────


class TestAdmin:
    @responses.activate
    def test_list_users(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/users",
            json=[
                {"id": "u-1", "username": "alice", "role": "admin"},
                {"id": "u-2", "username": "bob", "role": "user"},
            ],
        )
        users = authed_client.admin.list_users()
        assert len(users) == 2
        assert users[0].username == "alice"

    @responses.activate
    def test_delete_user(self, authed_client: GYDClient):
        responses.delete(
            f"{BASE}/users/u-2", json={"message": "user deleted"}
        )
        result = authed_client.admin.delete_user("u-2")
        assert result["message"] == "user deleted"

    @responses.activate
    def test_update_field_description(self, authed_client: GYDClient):
        responses.put(
            f"{BASE}/meta/brand",
            json={"message": "description updated"},
        )
        result = authed_client.admin.update_field_description(
            "brand", "brand or manufacturer"
        )
        assert result["message"] == "description updated"


# ── Token auto-refresh ───────────────────────────────────────────────────


class TestAutoRefresh:
    @responses.activate
    def test_auto_refresh_on_401(self, authed_client: GYDClient):
        # First call returns 401
        responses.get(
            f"{BASE}/receipts",
            json={"error": "token expired"},
            status=401,
        )
        # Refresh succeeds
        responses.post(
            f"{BASE}/auth/refresh",
            json={
                "access_token": "at-new",
                "refresh_token": "rt-new",
                "token_type": "Bearer",
            },
        )
        # Retry succeeds
        responses.get(f"{BASE}/receipts", json=[SAMPLE_RECEIPT])

        items = authed_client.receipts.list()
        assert len(items) == 1
