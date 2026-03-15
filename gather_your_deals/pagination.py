"""Pagination utilities for the GatherYourDeals SDK.

Provides :class:`PageIterator`, a lazy iterator that transparently
fetches paginated results from the API one page at a time, yielding
individual items.
"""

from typing import Any, Callable, Generic, Iterator, TypeVar

from gather_your_deals.http import HttpTransport

T = TypeVar("T")

_PAGE_SIZE = 50
"""Fixed page size used for all paginated requests."""


class PageIterator(Generic[T]):
    """Lazy iterator over a paginated API endpoint.

    Fetches pages of :data:`_PAGE_SIZE` items on demand, yielding one
    item at a time.  Pagination metadata (``total``, ``total_pages``)
    becomes available after the first page is fetched.

    :param transport: The shared HTTP transport instance.
    :param path: API endpoint path (e.g. ``"/receipts"``).
    :param params: Extra query parameters (``sort_by``, ``sort_order``, etc.).
        ``offset`` and ``limit`` are managed automatically.
    :param item_factory: Callable that converts a raw dict into a model
        instance (e.g. ``Receipt.from_dict``).

    Usage::

        for receipt in page_iter:
            print(receipt.product_name)

        # After iterating (or after at least one page has been fetched):
        print(page_iter.total)        # e.g. 120
        print(page_iter.total_pages)  # e.g. 3
    """

    def __init__(
        self,
        transport: HttpTransport,
        path: str,
        params: dict[str, Any],
        item_factory: Callable[[dict[str, Any]], T],
    ) -> None:
        self._transport = transport
        self._path = path
        self._params = params
        self._item_factory = item_factory
        self._total: int | None = None
        self._total_pages: int | None = None

    # ── Public metadata ──────────────────────────────────────────────

    @property
    def total(self) -> int | None:
        """Total number of items on the server.

        Returns ``None`` until the first page has been fetched.
        """
        return self._total

    @property
    def total_pages(self) -> int | None:
        """Total number of pages on the server.

        Returns ``None`` until the first page has been fetched.
        """
        return self._total_pages

    # ── Iteration ────────────────────────────────────────────────────

    def __iter__(self) -> Iterator[T]:
        offset = 0
        while True:
            params = {**self._params, "offset": offset, "limit": _PAGE_SIZE}
            data = self._transport.request("GET", self._path, params=params)

            self._total = data["total"]
            self._total_pages = data["total_pages"]

            items: list[dict[str, Any]] = data["data"]
            if not items:
                break

            for item in items:
                yield self._item_factory(item)

            offset += _PAGE_SIZE
            if offset >= self._total:
                break
