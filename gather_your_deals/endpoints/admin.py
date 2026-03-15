"""Admin-only endpoints for user and meta management."""

from typing import Any

from gather_your_deals.http import HttpTransport
from gather_your_deals.models import User
from gather_your_deals.pagination import PageIterator


class AdminEndpoint:
    """Admin-only operations: user management and meta field updates.

    All methods require the authenticated user to have the ``admin`` role.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    # ── User management ──────────────────────────────────────────────

    def list_users(
        self,
        *,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PageIterator[User]:
        """List all registered user accounts.

        Returns a lazy iterator that fetches pages of 50 items on demand.

        :param sort_by: Field to sort by.  Allowed values:
            ``created_at``, ``username``, ``role``.
        :param sort_order: Sort direction — ``"asc"`` or ``"desc"``.
        :returns: A :class:`~gather_your_deals.pagination.PageIterator`
            yielding :class:`~gather_your_deals.models.User` instances.
        :raises AuthorizationError: If the caller is not an admin.
        :raises AuthenticationError: If not authenticated.
        """
        params: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        return PageIterator(self._t, "/users", params, User.from_dict)

    def delete_user(self, user_id: str) -> dict[str, Any]:
        """Delete a user account and revoke all their refresh tokens.

        :param user_id: UUID of the user to delete.
        :returns: Response message dict.
        :raises AuthorizationError: If the caller is not an admin.
        :raises NotFoundError: If the user does not exist.
        :raises AuthenticationError: If not authenticated.
        """
        result: dict[str, Any] = self._t.request("DELETE", f"/users/{user_id}")
        return result

    # ── Meta management ──────────────────────────────────────────────

    def update_field_description(
        self,
        field_name: str,
        description: str,
    ) -> dict[str, Any]:
        """Update the description of an existing field.

        Works for both native and user-defined fields.

        :param field_name: The field to update.
        :param description: New description text.
        :returns: Response message dict.
        :raises AuthorizationError: If the caller is not an admin.
        :raises NotFoundError: If the field does not exist.
        :raises ValidationError: If the description is missing.
        :raises AuthenticationError: If not authenticated.
        """
        result: dict[str, Any] = self._t.request(
            "PUT",
            f"/meta/{field_name}",
            json={"description": description},
        )
        return result
