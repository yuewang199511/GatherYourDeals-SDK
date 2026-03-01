"""High-level SDK client for the GatherYourDeals Data API.

Typical usage::

    from gather_your_deals import GYDClient

    client = GYDClient("http://localhost:8080/api/v1")

    # Register + login
    client.users.register("alice", "password123")
    client.login("alice", "password123")

    # Create a receipt
    receipt = client.receipts.create(
        product_name="Milk 2%",
        purchase_date="2025.04.05",
        price="5.49CAD",
        amount="2lb",
        store_name="Costco",
    )

    # List receipts
    for r in client.receipts.list():
        print(r.product_name, r.price)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gather_your_deals.config import (
    clear_tokens,
    load_config,
    save_tokens,
)
from gather_your_deals.endpoints.admin import AdminEndpoint
from gather_your_deals.endpoints.meta import MetaEndpoint
from gather_your_deals.endpoints.receipts import ReceiptsEndpoint
from gather_your_deals.endpoints.sessions import SessionsEndpoint
from gather_your_deals.endpoints.users import UsersEndpoint
from gather_your_deals.http import HttpTransport
from gather_your_deals.models import TokenResponse


class GYDClient:
    """Top-level client for the GatherYourDeals Data API.

    :param base_url: API base URL.  If ``None``, the value from the
        config file (or the default ``http://localhost:8080/api/v1``)
        is used.
    :param timeout: Request timeout in seconds.  Overrides the config
        file value when specified.
    :param config_path: Override the default ``~/.GYD_SDK/env.yaml``
        config file path (mainly for testing).
    :param auto_persist_tokens: When ``True`` (the default), tokens
        are automatically saved to / loaded from the config file.

    The client exposes the following endpoint groups as attributes:

    * :attr:`users` — :class:`~gather_your_deals.endpoints.users.UsersEndpoint`
    * :attr:`sessions` — :class:`~gather_your_deals.endpoints.sessions.SessionsEndpoint`
    * :attr:`meta` — :class:`~gather_your_deals.endpoints.meta.MetaEndpoint`
    * :attr:`receipts` — :class:`~gather_your_deals.endpoints.receipts.ReceiptsEndpoint`
    * :attr:`admin` — :class:`~gather_your_deals.endpoints.admin.AdminEndpoint`
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: int | None = None,
        config_path: Path | None = None,
        auto_persist_tokens: bool = True,
    ):
        self._config_path = config_path
        self._auto_persist = auto_persist_tokens
        cfg = load_config(config_path)

        resolved_url = base_url or cfg.get("base_url", "http://localhost:8080/api/v1")
        resolved_timeout = timeout if timeout is not None else cfg.get("timeout", 30)

        self._transport = HttpTransport(resolved_url, resolved_timeout)

        # Wire up auto-persist callback
        if auto_persist_tokens:
            self._transport._on_token_refresh = self._on_token_refresh

        # Restore tokens from config if available
        stored_access = cfg.get("token")
        stored_refresh = cfg.get("refresh_token")
        if stored_access and stored_refresh:
            self._transport.set_tokens(stored_access, stored_refresh)

        # Endpoint groups
        self.users = UsersEndpoint(self._transport)
        self.sessions = SessionsEndpoint(self._transport)
        self.meta = MetaEndpoint(self._transport)
        self.receipts = ReceiptsEndpoint(self._transport)
        self.admin = AdminEndpoint(self._transport)

    # ── Convenience auth methods ─────────────────────────────────────

    def login(self, username: str, password: str) -> TokenResponse:
        """Log in and store the resulting tokens.

        This is a convenience method that calls
        :meth:`sessions.login <gather_your_deals.endpoints.sessions.SessionsEndpoint.login>`
        and automatically configures the client for authenticated requests.

        :param username: Account username.
        :param password: Account password.
        :returns: The :class:`~gather_your_deals.models.TokenResponse`.
        """
        tokens = self.sessions.login(username, password)
        self._transport.set_tokens(tokens.access_token, tokens.refresh_token)
        if self._auto_persist:
            save_tokens(tokens.access_token, tokens.refresh_token, self._config_path)
        return tokens

    def logout(self) -> dict[str, Any]:
        """Log out: revoke the refresh token and clear stored tokens.

        :returns: Response message dict.
        """
        refresh = self._transport._refresh_token
        result = self.sessions.logout(refresh)
        self._transport.clear_tokens()
        if self._auto_persist:
            clear_tokens(self._config_path)
        return result

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Manually set tokens (e.g. loaded from external storage).

        :param access_token: JWT access token.
        :param refresh_token: Refresh token.
        """
        self._transport.set_tokens(access_token, refresh_token)
        if self._auto_persist:
            save_tokens(access_token, refresh_token, self._config_path)

    def me(self) -> dict[str, Any]:
        """Shortcut for :meth:`sessions.me`."""
        return self.sessions.me()

    # ── Internal ─────────────────────────────────────────────────────

    def _on_token_refresh(self, access_token: str, refresh_token: str) -> None:
        """Callback invoked by the transport after an automatic token refresh."""
        save_tokens(access_token, refresh_token, self._config_path)

    @property
    def base_url(self) -> str:
        """The API base URL this client is connected to."""
        return self._transport.base_url

    @property
    def is_authenticated(self) -> bool:
        """``True`` if the client has an access token loaded."""
        return self._transport._access_token is not None
