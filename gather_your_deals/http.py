"""Low-level HTTP transport with automatic token refresh.

This module is internal.  Users should interact with
:class:`gather_your_deals.client.GYDClient` instead.
"""

from typing import Any

import requests

from gather_your_deals.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ConnectionError,
    GYDError,
    NotFoundError,
    ValidationError,
)

_STATUS_MAP: dict[int, type[GYDError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    409: ConflictError,
}


class HttpTransport:
    """Thin wrapper around :mod:`requests` that adds auth headers,
    automatic token refresh, and consistent error handling.

    :param base_url: API base URL (e.g. ``http://localhost:8080/api/v1``).
    :param timeout: Default request timeout in seconds.
    """

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._on_token_refresh: Any = None  # callback set by client

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Store the current token pair in memory."""
        self._access_token = access_token
        self._refresh_token = refresh_token

    def clear_tokens(self) -> None:
        """Remove in-memory tokens."""
        self._access_token = None
        self._refresh_token = None

    def _headers(self, authenticated: bool) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if authenticated and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _handle_response(self, resp: requests.Response) -> Any:
        """Parse a response, raising typed exceptions on error status."""
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = {"error": resp.text}
            msg = body.get("error", resp.text)
            exc_cls = _STATUS_MAP.get(resp.status_code, GYDError)
            raise exc_cls(msg, status_code=resp.status_code, response_body=body)
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    def _try_refresh(self) -> bool:
        """Attempt to refresh the access token using the stored refresh token.

        :returns: ``True`` if the refresh succeeded.
        """
        if not self._refresh_token:
            return False
        try:
            resp = requests.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self._refresh_token},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            if resp.status_code != 200:
                return False
            data = resp.json()
            self._access_token = data["access_token"]
            self._refresh_token = data["refresh_token"]
            if self._on_token_refresh:
                self._on_token_refresh(self._access_token, self._refresh_token)
            return True
        except requests.RequestException:
            return False

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> Any:
        """Send an HTTP request to the API.

        If a 401 is received and a refresh token is available, one
        automatic retry is attempted after refreshing the access token.

        :param method: HTTP method (``GET``, ``POST``, ``PUT``, ``DELETE``).
        :param path: URL path relative to :attr:`base_url`.
        :param json: JSON request body.
        :param authenticated: Whether to include the ``Authorization`` header.
        :returns: Parsed JSON response.
        :raises ConnectionError: If the server cannot be reached.
        :raises GYDError: On any API error response.
        """
        url = f"{self.base_url}{path}"
        try:
            resp = requests.request(
                method,
                url,
                json=json,
                headers=self._headers(authenticated),
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ConnectionError(f"Cannot reach {url}: {exc}") from exc

        # Auto-refresh on 401
        if resp.status_code == 401 and authenticated and self._try_refresh():
            try:
                resp = requests.request(
                    method,
                    url,
                    json=json,
                    headers=self._headers(authenticated),
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise ConnectionError(f"Cannot reach {url}: {exc}") from exc

        return self._handle_response(resp)
