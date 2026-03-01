"""User registration endpoint."""

from gather_your_deals.http import HttpTransport
from gather_your_deals.models import User


class UsersEndpoint:
    """Handles user registration.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    def register(self, username: str, password: str) -> User:
        """Register a new user account.

        :param username: Desired username.
        :param password: Password (minimum 8 characters).
        :returns: The created :class:`~gather_your_deals.models.User`.
        :raises ValidationError: If fields are missing or password is too short.
        :raises ConflictError: If the username is already taken.
        """
        data = self._t.request(
            "POST",
            "/users",
            json={"username": username, "password": password},
            authenticated=False,
        )
        return User.from_dict(data)
