"""Receipt (purchase record) endpoints."""

from typing import TYPE_CHECKING, Any, cast

from gather_your_deals.models import Receipt

if TYPE_CHECKING:
    from gather_your_deals.http import HttpTransport


class ReceiptsEndpoint:
    """Create, list, get, and delete purchase records.

    :param transport: The shared HTTP transport instance.
    """

    def __init__(self, transport: HttpTransport):
        self._t = transport

    def create(
        self,
        product_name: str,
        purchase_date: str,
        price: str,
        amount: str,
        store_name: str,
        *,
        latitude: float | None = None,
        longitude: float | None = None,
        extras: dict[str, Any] | None = None,
    ) -> Receipt:
        """Create a new purchase record.

        The server assigns ``id``, ``uploadTime``, and ``userId``
        automatically.

        :param product_name: Name of the purchased item.
        :param purchase_date: Date in ``Y.M.D`` format (e.g. ``"2025.04.05"``).
        :param price: Price string with currency (e.g. ``"5.49CAD"``).
        :param amount: Quantity string (e.g. ``"1"`` or ``"2lb"``).
        :param store_name: Name of the store.
        :param latitude: Optional latitude coordinate.
        :param longitude: Optional longitude coordinate.
        :param extras: Additional user-defined fields.  Every key must be
            registered in the meta table beforehand.
        :returns: The created :class:`~gather_your_deals.models.Receipt`
            with server-assigned fields populated.
        :raises ValidationError: If required fields are missing or an
            extra field is not registered.
        :raises AuthenticationError: If not authenticated.
        """
        body: dict[str, Any] = {
            "productName": product_name,
            "purchaseDate": purchase_date,
            "price": price,
            "amount": amount,
            "storeName": store_name,
        }
        if latitude is not None:
            body["latitude"] = latitude
        if longitude is not None:
            body["longitude"] = longitude
        if extras:
            body.update(extras)

        data = self._t.request("POST", "/receipts", json=body)
        return Receipt.from_dict(data)

    def create_from_receipt(self, receipt: Receipt) -> Receipt:
        """Create a receipt from an existing :class:`Receipt` object.

        This is a convenience wrapper around :meth:`create` that
        serializes the model (excluding server-set fields) and sends it.

        :param receipt: A :class:`~gather_your_deals.models.Receipt`
            with at least the required native fields populated.
        :returns: The created receipt with server-assigned fields.
        """
        body = receipt.to_dict(include_server_fields=False)
        data = self._t.request("POST", "/receipts", json=body)
        return Receipt.from_dict(data)

    def list(self) -> list[Receipt]:
        """List all receipts belonging to the authenticated user.

        Results are ordered newest first.

        :returns: List of :class:`~gather_your_deals.models.Receipt`.
        :raises AuthenticationError: If not authenticated.
        """
        data = self._t.request("GET", "/receipts")
        return [Receipt.from_dict(item) for item in data]

    def get(self, receipt_id: str) -> Receipt:
        """Get a single receipt by ID.

        :param receipt_id: UUID of the receipt.
        :returns: The matching :class:`~gather_your_deals.models.Receipt`.
        :raises NotFoundError: If the receipt does not exist.
        :raises AuthenticationError: If not authenticated.
        """
        data = self._t.request("GET", f"/receipts/{receipt_id}")
        return Receipt.from_dict(data)

    def delete(self, receipt_id: str) -> dict[str, Any]:
        """Delete a receipt by ID.

        :param receipt_id: UUID of the receipt to delete.
        :returns: Response message dict.
        :raises NotFoundError: If the receipt does not exist.
        :raises AuthenticationError: If not authenticated.
        """
        return cast(dict[str, Any], self._t.request("DELETE", f"/receipts/{receipt_id}"))
