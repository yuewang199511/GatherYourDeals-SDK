Quick Start
===========

This page shows the most common workflows using both the Python client
and the CLI.

Python
------

.. code-block:: python

   from gather_your_deals import GYDClient

   client = GYDClient("http://localhost:8080/api/v1")

   # Register a new account
   client.users.register("alice", "password123")

   # Log in — tokens are saved to ~/.GYD_SDK/env.yaml automatically
   client.login("alice", "password123")

   # Register a custom field
   client.meta.register("brand", "brand of the product", "string")

   # Create a receipt (with an extra field)
   receipt = client.receipts.create(
       product_name="Milk 2%",
       purchase_date="2025.04.05",
       price="5.49CAD",
       amount="2lb",
       store_name="Costco",
       latitude=49.2827,
       longitude=-123.1207,
       extras={"brand": "Kirkland"},
   )

   # List all your receipts — returns a lazy PageIterator
   # that fetches pages of 50 items on demand
   for r in client.receipts.list():
       print(r.product_name, r.price, r.store_name)

   # Custom sort order
   for r in client.receipts.list(sort_by="price", sort_order="asc"):
       print(r.product_name, r.price)

   # Access pagination metadata after iterating
   page_iter = client.receipts.list()
   for r in page_iter:
       pass
   print(page_iter.total)        # total items on server
   print(page_iter.total_pages)  # total number of pages

   # Meta and admin lists also return PageIterators
   for f in client.meta.list(sort_by="name", sort_order="desc"):
       print(f.field_name, f.type)

   # Get a single receipt
   r = client.receipts.get(receipt.id)

   # Delete a receipt — raises ReceiptNotFoundError if the id does not exist
   client.receipts.delete(receipt.id)

   # Current user info
   print(client.me())

   # Log out
   client.logout()

Microservice / JWT initialisation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your service already holds a user's JWT (e.g. extracted from an
incoming request header), you can initialise the client directly without
calling ``login()``::

   client = GYDClient(
       "http://localhost:8080/api/v1",
       access_token="eyJhbGci...",   # JWT access token
       refresh_token="abc123...",    # optional but recommended
   )

   for r in client.receipts.list():
       print(r.product_name)

When ``refresh_token`` is omitted the client will raise
:py:class:`~gather_your_deals.exceptions.AuthenticationError` once the
access token expires.  Pass both tokens so the SDK can renew the session
transparently.  See :doc:`token_storage` for a full discussion.

CLI
---

.. note::

   If you installed via ``poetry install``, prefix every command below
   with ``poetry run`` (or activate the shell first with ``poetry shell``).
   If you installed via ``pip install -e .``, the commands work directly.

.. code-block:: bash

   # Set the API URL
   gatherYourDeals config http://localhost:8080/api/v1

   # Register and log in
   gatherYourDeals register -u alice -p password123
   gatherYourDeals login -u alice -p password123

   # Current user
   gatherYourDeals me

   # Meta fields
   gatherYourDeals meta list
   gatherYourDeals meta add brand "brand of the product" --type string

   # Create a receipt
   gatherYourDeals receipts add \
       -n "Milk 2%" -d 2025.04.05 -p "5.49CAD" -a "2lb" -s "Costco" \
       --lat 49.2827 --lon -123.1207 \
       -e brand=Kirkland

   # List (shows 20 at a time — press Enter for more, Ctrl+C to stop)
   gatherYourDeals receipts list
   gatherYourDeals receipts get <receipt-id>
   gatherYourDeals receipts delete <receipt-id>

   # Bulk import from a JSON file
   gatherYourDeals receipts import receipts.json

   # Admin commands
   gatherYourDeals admin users
   gatherYourDeals admin delete-user <user-id>
   gatherYourDeals admin update-field brand "brand or manufacturer"

   # Show the stored JWT (useful for passing to another service)
   gatherYourDeals show-token           # prints the access token
   gatherYourDeals show-token --refresh # also prints the refresh token

   # Log out
   gatherYourDeals logout
