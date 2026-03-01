"""Admin-only endpoints for user and meta management."""

from typing import Any

from gather_your_deals.http import HttpTransport
from gather_your_deals.models import User


class AdminEndpoint:
    """Admin-only operations: user management and meta field updates.

    All methods require the authenticated user to have the ``admin`` role.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    # ── User management ──────────────────────────────────────────────

    def list_users(self) -> list[User]:
        """List all registered user accounts.

        :returns: List of :class:`~gather_your_deals.models.User`.
        :raises AuthorizationError: If the caller is not an admin.
        :raises AuthenticationError: If not authenticated.
        """
        data = self._t.request("GET", "/users")
        return [User.from_dict(item) for item in data]

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
