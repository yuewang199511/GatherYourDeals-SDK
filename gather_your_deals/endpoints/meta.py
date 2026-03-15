"""Field metadata endpoints."""

from typing import Any

from gather_your_deals.http import HttpTransport
from gather_your_deals.models import MetaField
from gather_your_deals.pagination import PageIterator


class MetaEndpoint:
    """Manage field definitions in the meta table.

    Any authenticated user can list and register fields.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    def list(
        self,
        *,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> PageIterator[MetaField]:
        """List all registered fields (native and user-defined).

        Returns a lazy iterator that fetches pages of 50 items on demand.

        :param sort_by: Field to sort by.  Allowed values: ``name``.
        :param sort_order: Sort direction — ``"asc"`` or ``"desc"``.
        :returns: A :class:`~gather_your_deals.pagination.PageIterator`
            yielding :class:`~gather_your_deals.models.MetaField` instances.
        :raises AuthenticationError: If not authenticated.
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        return PageIterator(self._t, "/meta", params, MetaField.from_dict)

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
