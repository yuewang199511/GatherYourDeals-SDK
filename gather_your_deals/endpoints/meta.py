"""Field metadata endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gather_your_deals.models import MetaField

if TYPE_CHECKING:
    from gather_your_deals.http import HttpTransport


class MetaEndpoint:
    """Manage field definitions in the meta table.

    Any authenticated user can list and register fields.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    def list(self) -> list[MetaField]:
        """List all registered fields (native and user-defined).

        :returns: List of :class:`~gather_your_deals.models.MetaField`.
        :raises AuthenticationError: If not authenticated.
        """
        data = self._t.request("GET", "/meta")
        return [MetaField.from_dict(item) for item in data]

    def register(self, field_name: str, description: str, field_type: str) -> MetaField:
        """Register a new user-defined field.

        Once registered, receipts can include this field.

        :param field_name: Name for the new field (e.g. ``"brand"``).
        :param description: Human-readable description.
        :param field_type: General type string (e.g. ``"string"``).
        :returns: The created :class:`~gather_your_deals.models.MetaField`.
        :raises ValidationError: If required fields are missing.
        :raises ConflictError: If the field already exists.
        :raises AuthenticationError: If not authenticated.
        """
        data = self._t.request(
            "POST",
            "/meta",
            json={
                "fieldName": field_name,
                "description": description,
                "type": field_type,
            },
        )
        return MetaField.from_dict(data)
