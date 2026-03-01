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

   # List all your receipts
   for r in client.receipts.list():
       print(r.product_name, r.price, r.store_name)

   # Get a single receipt
   r = client.receipts.get(receipt.id)

   # Delete a receipt
   client.receipts.delete(receipt.id)

   # Current user info
   print(client.me())

   # Log out
   client.logout()

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

   # List, get, delete
   gatherYourDeals receipts list
   gatherYourDeals receipts get <receipt-id>
   gatherYourDeals receipts delete <receipt-id>

   # Bulk import from a JSON file
   gatherYourDeals receipts import receipts.json

   # Admin commands
   gatherYourDeals admin users
   gatherYourDeals admin delete-user <user-id>
   gatherYourDeals admin update-field brand "brand or manufacturer"

   # Log out
   gatherYourDeals logout
