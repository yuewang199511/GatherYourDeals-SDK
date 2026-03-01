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

Custom config path
------------------

For testing or multi-environment setups you can override the file path:

.. code-block:: python

   from pathlib import Path

   client = GYDClient(config_path=Path("/tmp/test_env.yaml"))
