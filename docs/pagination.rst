Pagination
==========

All list endpoints in the API return paginated responses.  The SDK
handles this transparently through the
:py:class:`~gather_your_deals.pagination.PageIterator` class — a lazy
iterator that fetches pages behind the scenes and yields one item at a
time.

How it works
------------

When you call a ``list()`` method, no network request is made
immediately.  The first page is fetched when you start iterating.
Subsequent pages are fetched automatically as you consume items.

.. code-block:: python

   from gather_your_deals import GYDClient

   client = GYDClient()

   # Nothing is fetched yet
   page_iter = client.receipts.list()

   # First page (50 items) is fetched here
   for receipt in page_iter:
       print(receipt.product_name, receipt.price)
       # When item 51 is requested, the second page is fetched
       # automatically, and so on.

The fixed page size is **50 items** per API request.  This is handled
internally and cannot be changed by the caller.

Pagination metadata
-------------------

After at least one page has been fetched, the iterator exposes metadata
from the API response:

.. code-block:: python

   page_iter = client.receipts.list()

   # Before iteration — metadata is not yet available
   assert page_iter.total is None
   assert page_iter.total_pages is None

   for r in page_iter:
       pass

   # After iteration — metadata is populated
   print(page_iter.total)        # e.g. 120
   print(page_iter.total_pages)  # e.g. 3

Sorting
-------

All list methods accept ``sort_by`` and ``sort_order`` keyword arguments.
The allowed values match the API specification.

**Receipts:**

.. code-block:: python

   # Cheapest first
   for r in client.receipts.list(sort_by="price", sort_order="asc"):
       print(r.price)

   # Oldest purchases first
   for r in client.receipts.list(sort_by="purchase_date", sort_order="asc"):
       print(r.purchase_date)

Allowed ``sort_by`` values: ``created_at`` (default), ``purchase_date``,
``price``, ``store_name``, ``product_name``.

**Meta fields:**

.. code-block:: python

   for f in client.meta.list(sort_by="name", sort_order="desc"):
       print(f.field_name)

Allowed ``sort_by`` values: ``name`` (default).

**Admin — users:**

.. code-block:: python

   for u in client.admin.list_users(sort_by="username", sort_order="asc"):
       print(u.username)

Allowed ``sort_by`` values: ``created_at`` (default), ``username``,
``role``.

All endpoints default to ``sort_order="desc"`` except meta fields which
default to ``sort_order="asc"``.

Type hints
----------

``PageIterator`` is generic and exported from the top-level package, so
you can use it in type annotations:

.. code-block:: python

   from gather_your_deals import GYDClient, PageIterator, Receipt

   def show_all(items: PageIterator[Receipt]) -> None:
       for r in items:
           print(r.product_name)
       print(f"Total: {items.total}")

   client = GYDClient()
   show_all(client.receipts.list())

CLI scrolling
-------------

In the CLI, list commands display **20 items at a time**.  After each
batch you are prompted to press Enter for more or Ctrl+C to stop:

.. code-block:: text

   $ gatherYourDeals receipts list
     [a1b2c3d4] 2025.04.05  Milk 2%                          5.49CAD  @ Costco
     [b2c3d4e5] 2025.04.04  Eggs                              4.99CAD  @ Safeway
     ... (18 more rows)

   -- Showing 20 of 53 receipt(s). Press Enter for more, Ctrl+C to stop. --

     [c3d4e5f6] 2025.03.15  Bread                             3.49CAD  @ Costco
     ... (remaining rows)

   53 of 53 receipt(s).

This applies to ``receipts list``, ``meta list``, and ``admin users``.
