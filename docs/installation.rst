Installation
============

Requirements
------------

- Python 3.11+
- A running `GatherYourDeals Data API <https://github.com/yuewang199511/GatherYourDeals-data>`_ server

From source (Poetry)
--------------------

.. code-block:: bash

   git clone https://github.com/yuewang199511/GatherYourDeals-SDK.git
   cd GatherYourDeals-SDK
   poetry install

This installs the package into Poetry's virtual environment. You will
need to prefix commands with ``poetry run`` or activate the shell with
``poetry shell``.

From source (pip)
-----------------

If you prefer to install directly into your current environment (e.g.
conda, venv, or system Python):

.. code-block:: bash

   git clone https://github.com/yuewang199511/GatherYourDeals-SDK.git
   cd GatherYourDeals-SDK
   pip install -e .

The ``-e`` flag enables editable mode so code changes are reflected
immediately. With this approach the ``gatherYourDeals`` CLI is available
directly — no ``poetry run`` prefix needed.

Development extras
------------------

To install in editable mode with test and documentation dependencies:

.. code-block:: bash

   poetry install --with dev

Poetry installs the package in editable mode by default, so the
``gatherYourDeals`` CLI and all library imports always reflect your
latest code changes — no reinstall needed. Simply edit a source file,
save, and run again.

This pulls in ``pytest``, ``responses``, ``sphinx``, ``ruff``, ``mypy``,
and related tooling.

Verify the installation
-----------------------

.. code-block:: bash

   # If installed via pip install -e .
   gatherYourDeals --help

   # If installed via poetry install
   poetry run gatherYourDeals --help
   # or: poetry shell && gatherYourDeals --help

   # Verify the Python import
   python -c "from gather_your_deals import GYDClient; print('OK')"
