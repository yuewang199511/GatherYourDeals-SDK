"""Custom exceptions for the GatherYourDeals SDK."""

from typing import Any


class GYDError(Exception):
    """Base exception for all SDK errors.

    :param message: Human-readable error description.
    :param status_code: HTTP status code from the API response, if any.
    :param response_body: Raw response body dict, if available.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(GYDError):
    """Raised when authentication fails (401).

    Prefer the more specific subclasses when you need to distinguish
    the cause:

    * :class:`NotAuthenticatedError` — no token was present at all.
    * :class:`TokenExpiredError` — a token was sent but the server
      rejected it (typically because it expired).
    """


class NotAuthenticatedError(AuthenticationError):
    """Raised when a request requires authentication but no token is set.

    This means :py:meth:`~gather_your_deals.client.GYDClient.login` has
    not been called (or no ``access_token`` was passed to the client).
    """


class TokenExpiredError(AuthenticationError):
    """Raised when the server rejects the access token with a 401.

    The token was present but the server did not accept it — most
    commonly because the JWT has expired.  When no refresh token is
    configured the SDK raises this immediately rather than attempting a
    silent refresh.
    """


class AuthorizationError(GYDError):
    """Raised when the user lacks permission (403).

    Typically occurs when a non-admin user attempts
    an admin-only operation.
    """


class NotFoundError(GYDError):
    """Raised when a requested resource is not found (404)."""


class ConflictError(GYDError):
    """Raised on resource conflicts (409).

    Examples include duplicate usernames or
    already-registered meta fields.
    """


class ValidationError(GYDError):
    """Raised on invalid request data (400).

    This covers missing required fields, password too short,
    unregistered extra fields, etc.
    """


class ConfigError(GYDError):
    """Raised when SDK configuration is missing or invalid."""


class ConnectionError(GYDError):
    """Raised when the SDK cannot reach the API server."""
