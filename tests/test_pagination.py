"""Tests for the PageIterator pagination logic."""

from pathlib import Path

import pytest
import responses

from gather_your_deals.client import GYDClient

BASE = "http://localhost:8080/api/v1"


@pytest.fixture
def authed_client(tmp_path: Path) -> GYDClient:
    """Create a client pre-loaded with tokens."""
    c = GYDClient(BASE, config_path=tmp_path / "env.yaml", auto_persist_tokens=False)
    c.set_tokens("test-access", "test-refresh")
    return c


def _make_receipt(i: int) -> dict:
    return {
        "id": f"r-{i:03d}",
        "productName": f"Product {i}",
        "purchaseDate": "2025.04.05",
        "price": f"{i}.99CAD",
        "amount": "1",
        "storeName": "TestStore",
        "latitude": None,
        "longitude": None,
        "uploadTime": 1770620311 + i,
        "userId": "u-1",
    }


class TestMultiPageIteration:
    """Verify the generator correctly walks through multiple pages."""

    @responses.activate
    def test_three_pages(self, authed_client: GYDClient):
        """120 total items → 50 + 50 + 20 across three pages."""
        total = 120
        page1 = [_make_receipt(i) for i in range(50)]
        page2 = [_make_receipt(i) for i in range(50, 100)]
        page3 = [_make_receipt(i) for i in range(100, 120)]

        # Page 1: offset=0
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page1,
                "total": total,
                "offset": 0,
                "limit": 50,
                "total_pages": 3,
            },
        )
        # Page 2: offset=50
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page2,
                "total": total,
                "offset": 50,
                "limit": 50,
                "total_pages": 3,
            },
        )
        # Page 3: offset=100
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page3,
                "total": total,
                "offset": 100,
                "limit": 50,
                "total_pages": 3,
            },
        )

        page_iter = authed_client.receipts.list()
        items = list(page_iter)

        assert len(items) == 120
        assert items[0].id == "r-000"
        assert items[49].id == "r-049"
        assert items[50].id == "r-050"
        assert items[119].id == "r-119"
        assert page_iter.total == 120
        assert page_iter.total_pages == 3
        # Verify three GET requests were made
        assert len(responses.calls) == 3

    @responses.activate
    def test_exactly_one_page(self, authed_client: GYDClient):
        """50 items fits exactly in one page — no second request."""
        page1 = [_make_receipt(i) for i in range(50)]

        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page1,
                "total": 50,
                "offset": 0,
                "limit": 50,
                "total_pages": 1,
            },
        )

        items = list(authed_client.receipts.list())
        assert len(items) == 50
        assert len(responses.calls) == 1

    @responses.activate
    def test_empty_result(self, authed_client: GYDClient):
        """Zero items — single request, no items yielded."""
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": [],
                "total": 0,
                "offset": 0,
                "limit": 50,
                "total_pages": 0,
            },
        )

        page_iter = authed_client.receipts.list()
        items = list(page_iter)
        assert len(items) == 0
        assert page_iter.total == 0
        assert page_iter.total_pages == 0
        assert len(responses.calls) == 1

    @responses.activate
    def test_partial_last_page(self, authed_client: GYDClient):
        """53 items → page 1 has 50, page 2 has 3."""
        total = 53
        page1 = [_make_receipt(i) for i in range(50)]
        page2 = [_make_receipt(i) for i in range(50, 53)]

        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page1,
                "total": total,
                "offset": 0,
                "limit": 50,
                "total_pages": 2,
            },
        )
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": page2,
                "total": total,
                "offset": 50,
                "limit": 50,
                "total_pages": 2,
            },
        )

        items = list(authed_client.receipts.list())
        assert len(items) == 53
        assert len(responses.calls) == 2


class TestPageIteratorMetadata:
    """Verify that total/total_pages are None before iteration."""

    def test_metadata_none_before_iteration(self, authed_client: GYDClient):
        page_iter = authed_client.receipts.list()
        assert page_iter.total is None
        assert page_iter.total_pages is None


class TestSortParams:
    """Verify sort parameters are passed through to the API."""

    @responses.activate
    def test_receipts_custom_sort(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/receipts",
            json={
                "data": [_make_receipt(0)],
                "total": 1,
                "offset": 0,
                "limit": 50,
                "total_pages": 1,
            },
        )

        list(authed_client.receipts.list(sort_by="price", sort_order="asc"))

        # Check query params on the actual request
        req = responses.calls[0].request
        assert "sort_by=price" in req.url
        assert "sort_order=asc" in req.url

    @responses.activate
    def test_meta_default_sort(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/meta",
            json={
                "data": [],
                "total": 0,
                "offset": 0,
                "limit": 50,
                "total_pages": 0,
            },
        )

        list(authed_client.meta.list())

        req = responses.calls[0].request
        assert "sort_by=name" in req.url
        assert "sort_order=asc" in req.url

    @responses.activate
    def test_admin_users_custom_sort(self, authed_client: GYDClient):
        responses.get(
            f"{BASE}/users",
            json={
                "data": [],
                "total": 0,
                "offset": 0,
                "limit": 50,
                "total_pages": 0,
            },
        )

        list(authed_client.admin.list_users(sort_by="username", sort_order="asc"))

        req = responses.calls[0].request
        assert "sort_by=username" in req.url
        assert "sort_order=asc" in req.url
