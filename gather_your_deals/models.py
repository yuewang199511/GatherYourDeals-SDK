"""Data models for the GatherYourDeals SDK.

All models are plain dataclasses that mirror the API's JSON schemas.
They can be created from API response dicts via :meth:`from_dict`
and converted back via :meth:`to_dict`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class User:
    """A registered user account.

    :param id: UUID of the user.
    :param username: Login name.
    :param role: Either ``"admin"`` or ``"user"``.
    """

    id: str
    username: str
    role: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create a :class:`User` from an API response dict."""
        return cls(
            id=data["id"],
            username=data["username"],
            role=data["role"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {"id": self.id, "username": self.username, "role": self.role}


@dataclass
class TokenResponse:
    """Token pair returned by login and refresh endpoints.

    :param access_token: Short-lived JWT for authenticating requests.
    :param refresh_token: Long-lived token used to obtain a new access token.
    :param token_type: Always ``"Bearer"``.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TokenResponse:
        """Create a :class:`TokenResponse` from an API response dict."""
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data.get("token_type", "Bearer"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
        }


@dataclass
class MetaField:
    """A field definition from the meta table.

    :param field_name: Name of the field (e.g. ``"brand"``).
    :param description: Human-readable description.
    :param type: General type string (e.g. ``"string"``, ``"float"``).
    :param native: ``True`` for built-in fields that cannot be removed.
    """

    field_name: str
    description: str
    type: str
    native: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetaField:
        """Create a :class:`MetaField` from an API response dict."""
        return cls(
            field_name=data["fieldName"],
            description=data["description"],
            type=data["type"],
            native=data.get("native", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "fieldName": self.field_name,
            "description": self.description,
            "type": self.type,
            "native": self.native,
        }


@dataclass
class Receipt:
    """A purchase record.

    Native fields are stored as dedicated attributes.  Any additional
    user-defined fields are collected in :attr:`extras`.

    :param id: UUID of the receipt (server-assigned).
    :param product_name: Name of the purchased item.
    :param purchase_date: Date in ``Y.M.D`` format.
    :param price: Price string including currency (e.g. ``"5.49CAD"``).
    :param amount: Quantity string, e.g. ``"1"`` or ``"2lb"``.
    :param store_name: Name of the store.
    :param latitude: Optional latitude coordinate.
    :param longitude: Optional longitude coordinate.
    :param upload_time: Unix epoch seconds when the record was uploaded.
    :param user_id: UUID of the user who created this record.
    :param extras: User-defined fields registered in the meta table.
    """

    id: str = ""
    product_name: str = ""
    purchase_date: str = ""
    price: str = ""
    amount: str = ""
    store_name: str = ""
    latitude: float | None = None
    longitude: float | None = None
    upload_time: int | None = None
    user_id: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    _NATIVE_API_KEYS: frozenset[str] = frozenset(
        {
            "id",
            "productName",
            "purchaseDate",
            "price",
            "amount",
            "storeName",
            "latitude",
            "longitude",
            "uploadTime",
            "userId",
        }
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Receipt:
        """Create a :class:`Receipt` from an API response dict.

        Any keys that are not native fields are placed into
        :attr:`extras`.
        """
        extras = {k: v for k, v in data.items() if k not in cls._NATIVE_API_KEYS}
        return cls(
            id=data.get("id", ""),
            product_name=data.get("productName", ""),
            purchase_date=data.get("purchaseDate", ""),
            price=data.get("price", ""),
            amount=data.get("amount", ""),
            store_name=data.get("storeName", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            upload_time=data.get("uploadTime"),
            user_id=data.get("userId", ""),
            extras=extras,
        )

    def to_dict(self, include_server_fields: bool = True) -> dict[str, Any]:
        """Serialize to a flat dict matching the API format.

        :param include_server_fields: If ``False``, omit ``id``,
            ``uploadTime``, and ``userId`` (useful for create requests).
        """
        d: dict[str, Any] = {
            "productName": self.product_name,
            "purchaseDate": self.purchase_date,
            "price": self.price,
            "amount": self.amount,
            "storeName": self.store_name,
        }
        if self.latitude is not None:
            d["latitude"] = self.latitude
        if self.longitude is not None:
            d["longitude"] = self.longitude
        if include_server_fields:
            d["id"] = self.id
            d["uploadTime"] = self.upload_time
            d["userId"] = self.user_id
        d.update(self.extras)
        return d
