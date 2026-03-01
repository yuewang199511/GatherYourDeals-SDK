"""Custom exceptions for the GatherYourDeals SDK."""

from __future__ import annotations

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

    This includes invalid credentials, expired tokens,
    or missing authorization headers.
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
