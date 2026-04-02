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
   ├── ValidationError          (400)
   ├── AuthenticationError      (401 — catch-all)
   │   ├── NotAuthenticatedError  (no token set on the client)
   │   └── TokenExpiredError      (token sent but rejected by server)
   ├── AuthorizationError       (403)
   ├── NotFoundError            (404)
   ├── ConflictError            (409)
   ├── ConfigError              (config file issues)
   └── ConnectionError          (server unreachable)

Exception descriptions
----------------------

``GYDError``
   Base class for every SDK exception.  Carries three attributes available
   on all subclasses:

   * ``str(e)`` — human-readable message from the server or the SDK.
   * ``e.status_code`` — HTTP status code (``int``), or ``None`` for
     non-HTTP errors such as ``ConfigError`` and ``ConnectionError``.
   * ``e.response_body`` — parsed JSON body from the server (``dict``),
     or ``None`` when not applicable.

``ValidationError`` *(400)*
   The request was rejected because the data was invalid.  Common causes:
   missing required fields, a password shorter than 8 characters, or an
   extra field that has not been registered via ``meta.register()``.

``AuthenticationError`` *(401)*
   Catch-all for authentication failures.  Use the more specific subclasses
   below when you need to tell them apart.  Raised directly by
   ``login()`` when the credentials are wrong.

``NotAuthenticatedError`` *(401 — subclass of* ``AuthenticationError`` *)*
   Raised *before* any network call when an authenticated endpoint is
   invoked but no access token is set on the client.  This means
   ``login()`` was never called and no ``access_token=`` was passed to
   ``GYDClient``.

``TokenExpiredError`` *(401 — subclass of* ``AuthenticationError`` *)*
   Raised when an access token was sent to the server but was rejected
   with a 401.  This almost always means the JWT has expired.  When no
   refresh token is configured (the microservice pattern), the SDK raises
   this immediately so the caller knows to obtain a fresh token.  When a
   refresh token *is* configured, the SDK silently refreshes and retries
   first — this exception is only raised if the refresh itself also fails.

``AuthorizationError`` *(403)*
   The authenticated user does not have permission to perform the
   operation.  Typically raised when a non-admin user calls an
   admin-only endpoint such as ``admin.list_users()``.

``NotFoundError`` *(404)*
   The requested resource does not exist.  Raised when a receipt ID or
   user ID passed to ``get()``, ``delete()``, etc. is not found on the
   server.

``ConflictError`` *(409)*
   A uniqueness constraint was violated.  Raised when registering a
   username that is already taken, or adding a meta field that already
   exists.

``ConfigError`` *(no HTTP status)*
   The SDK config file (``~/.GYD_SDK/env.yaml``) exists but could not be
   parsed.  Usually caused by a manually edited or corrupted YAML file.

``ConnectionError`` *(no HTTP status)*
   The SDK could not reach the API server at all.  Possible causes: wrong
   ``base_url``, server not running, network timeout, or DNS failure.

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
     - ``AuthenticationError`` (or subclass)
     - ``NotAuthenticatedError``: no token set. ``TokenExpiredError``: token
       sent but server rejected it. ``AuthenticationError``: invalid
       credentials (e.g. wrong password on login).
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

**Distinguish token state in a microservice:**

.. code-block:: python

   from gather_your_deals import (
       GYDClient,
       NotAuthenticatedError,
       TokenExpiredError,
       AuthenticationError,
   )

   client = GYDClient(
       "http://localhost:8080/api/v1",
       access_token=jwt_from_request,
       auto_persist_tokens=False,
   )

   try:
       results = list(client.receipts.list())
   except NotAuthenticatedError:
       # No token was set at all — login flow was never completed
       raise RuntimeError("Client has no token; ensure access_token is passed.")
   except TokenExpiredError:
       # Token was present but the server rejected it
       raise RuntimeError("JWT expired — obtain a fresh token and retry.")
   except AuthenticationError:
       # Catch-all for any other 401 (e.g. invalid credentials on login)
       raise

**Catch all SDK errors:**

.. code-block:: python

   from gather_your_deals import GYDClient, GYDError

   client = GYDClient()

   try:
       for r in client.receipts.list():
           print(r.product_name)
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
