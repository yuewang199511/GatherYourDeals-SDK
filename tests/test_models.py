"""Tests for data models."""

from gather_your_deals.models import MetaField, Receipt, TokenResponse, User


class TestUser:
    def test_from_dict(self):
        data = {"id": "abc-123", "username": "alice", "role": "user"}
        user = User.from_dict(data)
        assert user.id == "abc-123"
        assert user.username == "alice"
        assert user.role == "user"

    def test_to_dict(self):
        user = User(id="abc-123", username="alice", role="admin")
        assert user.to_dict() == {"id": "abc-123", "username": "alice", "role": "admin"}


class TestTokenResponse:
    def test_from_dict(self):
        data = {
            "access_token": "at",
            "refresh_token": "rt",
            "token_type": "Bearer",
        }
        t = TokenResponse.from_dict(data)
        assert t.access_token == "at"
        assert t.refresh_token == "rt"
        assert t.token_type == "Bearer"

    def test_default_token_type(self):
        data = {"access_token": "at", "refresh_token": "rt"}
        t = TokenResponse.from_dict(data)
        assert t.token_type == "Bearer"


class TestMetaField:
    def test_from_dict(self):
        data = {
            "fieldName": "brand",
            "description": "brand of the product",
            "type": "string",
            "native": False,
        }
        f = MetaField.from_dict(data)
        assert f.field_name == "brand"
        assert f.description == "brand of the product"
        assert f.type == "string"
        assert f.native is False

    def test_to_dict(self):
        f = MetaField(field_name="brand", description="desc", type="string", native=True)
        assert f.to_dict() == {
            "fieldName": "brand",
            "description": "desc",
            "type": "string",
            "native": True,
        }


class TestReceipt:
    SAMPLE = {
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
        "brand": "Kirkland",
    }

    def test_from_dict_native_fields(self):
        r = Receipt.from_dict(self.SAMPLE)
        assert r.product_name == "Milk 2%"
        assert r.purchase_date == "2025.04.05"
        assert r.price == "5.49CAD"
        assert r.amount == "2lb"
        assert r.store_name == "Costco"
        assert r.latitude == 49.28
        assert r.longitude == -123.12
        assert r.upload_time == 1770620311
        assert r.user_id == "u-1"

    def test_from_dict_extras(self):
        r = Receipt.from_dict(self.SAMPLE)
        assert r.extras == {"brand": "Kirkland"}

    def test_to_dict_full(self):
        r = Receipt.from_dict(self.SAMPLE)
        d = r.to_dict(include_server_fields=True)
        assert d["id"] == "r-123"
        assert d["productName"] == "Milk 2%"
        assert d["brand"] == "Kirkland"

    def test_to_dict_without_server_fields(self):
        r = Receipt.from_dict(self.SAMPLE)
        d = r.to_dict(include_server_fields=False)
        assert "id" not in d
        assert "uploadTime" not in d
        assert "userId" not in d
        assert d["productName"] == "Milk 2%"
        assert d["brand"] == "Kirkland"

    def test_optional_location_fields(self):
        data = {
            "id": "r-2",
            "productName": "Bread",
            "purchaseDate": "2025.05.01",
            "price": "3.99CAD",
            "amount": "1",
            "storeName": "Safeway",
            "uploadTime": 1770620311,
            "userId": "u-1",
        }
        r = Receipt.from_dict(data)
        assert r.latitude is None
        assert r.longitude is None
        d = r.to_dict(include_server_fields=False)
        assert "latitude" not in d
        assert "longitude" not in d
