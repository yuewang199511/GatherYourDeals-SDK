Token Storage
=============

The SDK persists tokens and settings in a YAML file so that you don't
need to log in on every invocation.

File location
-------------

By default the config file lives at::

   ~/.GYD_SDK/env.yaml

The directory and file are created automatically on first write.

File format
-----------

.. code-block:: yaml

   base_url: "http://localhost:8080/api/v1"
   timeout: 30
   token: "your-access-token"
   refresh_token: "your-refresh-token"

``token`` is the short-lived JWT access token.  ``refresh_token`` is the
long-lived token used to obtain a new pair when the access token expires.

How it works
------------

When you call :py:meth:`~gather_your_deals.client.GYDClient.login` (or
run ``gatherYourDeals login`` in the CLI), both tokens are written to the
config file.  On the next ``GYDClient()`` instantiation the stored tokens
are loaded automatically, so the client is ready to make authenticated
requests without calling ``login()`` again.

When the access token expires and the SDK refreshes it (see
:doc:`lazy_login`), the new pair is persisted as well.

Calling :py:meth:`~gather_your_deals.client.GYDClient.logout` (or
``gatherYourDeals logout``) revokes the refresh token on the server and
removes both tokens from the file.

Disabling auto-persistence
--------------------------

If you manage tokens yourself (for example in a web backend that stores
them in a database), pass ``auto_persist_tokens=False``:

.. code-block:: python

   client = GYDClient(
       "http://localhost:8080/api/v1",
       auto_persist_tokens=False,
   )

   # Manually supply tokens
   client.set_tokens(access_token="...", refresh_token="...")

Microservice / JWT initialisation
----------------------------------

In a microservice you may already hold a user's tokens obtained upstream
(e.g. forwarded from a gateway or extracted from a request header).
Pass them directly to ``GYDClient`` to skip the login round-trip:

.. code-block:: python

   client = GYDClient(
       "http://localhost:8080/api/v1",
       access_token="eyJhbGci...",   # JWT access token
       refresh_token="abc123...",    # optional — enables auto-refresh
   )

When ``access_token`` is supplied it takes priority over any tokens
stored in the config file.

**Do I need the refresh token?**

+----------------------------------+------------------------------------------+
| Scenario                         | Recommendation                           |
+==================================+==========================================+
| Short-lived request handler      | ``access_token`` only is fine            |
+----------------------------------+------------------------------------------+
| Long-running service / worker    | Pass **both** tokens; the SDK will       |
|                                  | renew the session transparently on expiry|
+----------------------------------+------------------------------------------+

The refresh token is never sent in a header.  When needed, the SDK posts
it to ``POST /auth/refresh`` in the request body and updates both tokens
in memory (and on disk when ``auto_persist_tokens=True``).

Retrieving the stored token from the CLI
-----------------------------------------

Use ``show-token`` to print the token saved by a previous ``login`` call
so you can pass it to another service:

.. code-block:: bash

   # Print the access token
   gatherYourDeals show-token

   # Also print the refresh token
   gatherYourDeals show-token --refresh

   # Capture in a variable
   ACCESS=$(gatherYourDeals show-token)
   REFRESH=$(gatherYourDeals show-token --refresh | tail -1)

Custom config path
------------------

For testing or multi-environment setups you can override the file path:

.. code-block:: python

   from pathlib import Path

   client = GYDClient(config_path=Path("/tmp/test_env.yaml"))
