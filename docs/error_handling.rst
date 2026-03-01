Error Handling
==============

The SDK maps every HTTP error status from the API to a typed Python
exception.  All exceptions inherit from
:py:class:`~gather_your_deals.exceptions.GYDError`, so you can catch
that base class for a blanket handler or catch specific subclasses for
fine-grained control.

Exception hierarchy
-------------------

.. code-block:: text

   GYDError
   ├── ValidationError        (400)
   ├── AuthenticationError     (401)
   ├── AuthorizationError      (403)
   ├── NotFoundError           (404)
   ├── ConflictError           (409)
   ├── ConfigError             (config file issues)
   └── ConnectionError         (server unreachable)

Status code mapping
-------------------

.. list-table::
   :header-rows: 1
   :widths: 15 30 55

   * - HTTP Status
     - Exception
     - Typical cause
   * - 400
     - ``ValidationError``
     - Missing required fields, password too short, unregistered extra field
   * - 401
     - ``AuthenticationError``
     - Invalid credentials, expired token, missing ``Authorization`` header
   * - 403
     - ``AuthorizationError``
     - Non-admin user calling an admin-only endpoint
   * - 404
     - ``NotFoundError``
     - Receipt or user ID does not exist
   * - 409
     - ``ConflictError``
     - Duplicate username or already-registered meta field

Non-HTTP exceptions:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Exception
     - Typical cause
   * - ``ConfigError``
     - ``~/.GYD_SDK/env.yaml`` exists but cannot be parsed
   * - ``ConnectionError``
     - The API server is unreachable (network error, wrong URL, timeout)

Exception attributes
--------------------

Every exception carries extra context you can inspect:

.. code-block:: python

   from gather_your_deals import GYDClient, GYDError

   client = GYDClient()

   try:
       client.receipts.get("bad-id")
   except GYDError as e:
       print(e)                  # human-readable message
       print(e.status_code)      # e.g. 404
       print(e.response_body)    # e.g. {"error": "receipt not found"}

Usage examples
--------------

**Catch a specific error:**

.. code-block:: python

   from gather_your_deals import GYDClient, AuthenticationError

   client = GYDClient()

   try:
       client.login("alice", "wrong-password")
   except AuthenticationError as e:
       print(f"Login failed: {e}")

**Catch all SDK errors:**

.. code-block:: python

   from gather_your_deals import GYDClient, GYDError

   client = GYDClient()

   try:
       client.receipts.list()
   except GYDError as e:
       print(f"API error ({e.status_code}): {e}")

**Handle conflict on registration:**

.. code-block:: python

   from gather_your_deals import GYDClient, ConflictError

   client = GYDClient()

   try:
       client.users.register("alice", "password123")
   except ConflictError:
       print("Username already taken — try a different one.")

**Handle missing resources:**

.. code-block:: python

   from gather_your_deals import GYDClient, NotFoundError

   client = GYDClient()

   try:
       client.receipts.delete("nonexistent-id")
   except NotFoundError:
       print("Receipt does not exist.")

CLI error output
----------------

In the CLI, all ``GYDError`` exceptions are caught and printed to
stderr with a non-zero exit code, so you can use standard shell error
handling:

.. code-block:: bash

   gatherYourDeals receipts get bad-id || echo "failed"
