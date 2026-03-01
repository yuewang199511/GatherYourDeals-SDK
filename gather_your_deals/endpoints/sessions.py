"""Authentication and session endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from gather_your_deals.models import TokenResponse

if TYPE_CHECKING:
    from gather_your_deals.http import HttpTransport


class SessionsEndpoint:
    """Handles login, logout, token refresh, and current-user queries.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    def login(self, username: str, password: str) -> TokenResponse:
        """Authenticate and obtain a token pair.

        :param username: Account username.
        :param password: Account password.
        :returns: A :class:`~gather_your_deals.models.TokenResponse`
            containing the access and refresh tokens.
        :raises AuthenticationError: If the credentials are invalid.
        """
        data = self._t.request(
            "POST",
            "/auth/login",
            json={"username": username, "password": password},
            authenticated=False,
        )
        return TokenResponse.from_dict(data)

    def logout(self, refresh_token: str | None = None) -> dict[str, Any]:
        """Revoke the refresh token and end the session.

        :param refresh_token: The refresh token to revoke.  If ``None``,
            the access token will simply expire on its own.
        :returns: Response message dict.
        """
        body: dict[str, Any] = {}
        if refresh_token:
            body["refresh_token"] = refresh_token
        return cast(dict[str, Any], self._t.request("POST", "/auth/logout", json=body))

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Exchange a refresh token for a new token pair.

        The old refresh token is immediately invalidated (rotation).

        :param refresh_token: Current valid refresh token.
        :returns: A new :class:`~gather_your_deals.models.TokenResponse`.
        :raises AuthenticationError: If the refresh token is invalid or expired.
        """
        data = self._t.request(
            "POST",
            "/auth/refresh",
            json={"refresh_token": refresh_token},
            authenticated=False,
        )
        return TokenResponse.from_dict(data)

    def me(self) -> dict[str, Any]:
        """Get the current authenticated user's ID and role.

        :returns: Dict with ``id`` and ``role`` keys.
        :raises AuthenticationError: If not authenticated.
        """
        return cast(dict[str, Any], self._t.request("GET", "/auth/me"))
