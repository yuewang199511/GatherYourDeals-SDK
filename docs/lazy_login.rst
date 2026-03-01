Lazy Login
==========

The SDK uses a **lazy login** strategy: tokens are stored at login time
but are only verified when an actual API request is sent.

CLI flow
--------

When you run ``gatherYourDeals login``, the SDK calls the
``POST /auth/login`` endpoint and saves both tokens to
``~/.GYD_SDK/env.yaml``.  Subsequent commands (``receipts list``,
``meta list``, etc.) read the stored token and include it in the
``Authorization`` header — no second login call is made.

.. code-block:: bash

   gatherYourDeals login -u alice -p password123   # token saved
   gatherYourDeals receipts list                    # token used here

If the server rejects the token (for example because it has expired),
the SDK handles it transparently via automatic refresh.

Automatic token refresh
-----------------------

Whenever an authenticated request receives a **401 Unauthorized**
response, the SDK:

1. Sends a ``POST /auth/refresh`` request using the stored refresh token.
2. If the refresh succeeds, stores the new token pair (both in memory and
   on disk when ``auto_persist_tokens`` is enabled).
3. Retries the original request with the new access token.

If the refresh itself fails (for example the refresh token is also
expired or revoked), the SDK raises
:py:class:`~gather_your_deals.exceptions.AuthenticationError` so you
know a new ``login()`` call is needed.

.. code-block:: python

   from gather_your_deals import GYDClient, AuthenticationError

   client = GYDClient()  # loads saved tokens

   try:
       receipts = client.receipts.list()
   except AuthenticationError:
       # Both tokens expired — prompt the user to log in again
       client.login("alice", "password123")
       receipts = client.receipts.list()

Python flow
-----------

The same lazy behaviour applies when using ``GYDClient`` directly.
Constructing the client loads tokens from the config file but makes no
network calls.  The first ``client.receipts.list()`` (or any other
endpoint method) is what actually reaches out to the server.

.. code-block:: python

   client = GYDClient()          # no network call
   client.receipts.list()        # token verified here

Refresh callback
----------------

Internally, the HTTP transport fires an ``_on_token_refresh`` callback
after a successful refresh.  When ``auto_persist_tokens=True`` (the
default), this callback writes the new pair to the config file so that
the next process that creates a ``GYDClient`` picks up the fresh tokens
automatically.
