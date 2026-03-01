"""GatherYourDeals SDK — Python client for the GatherYourDeals Data API.

Quick start::

    from gather_your_deals import GYDClient

    client = GYDClient("http://localhost:8080/api/v1")
    client.login("alice", "password123")

    for receipt in client.receipts.list():
        print(receipt.product_name, receipt.price)
"""

from importlib.metadata import version

__version__ = version("gather-your-deals")

from gather_your_deals.client import GYDClient
from gather_your_deals.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigError,
    ConflictError,
    ConnectionError,
    GYDError,
    NotFoundError,
    ValidationError,
)
from gather_your_deals.models import MetaField, Receipt, TokenResponse, User

__all__ = [
    "__version__",
    "GYDClient",
    # Models
    "User",
    "TokenResponse",
    "MetaField",
    "Receipt",
    # Exceptions
    "GYDError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "ConfigError",
    "ConnectionError",
]
