# GatherYourDeals SDK

Python SDK for the [GatherYourDeals Data API](https://github.com/yuewang199511/GatherYourDeals-data).

Supports all exposed API endpoints: user registration, authentication with automatic token refresh, field metadata management, receipt CRUD, and admin operations.

## Installation

```bash
git clone https://github.com/yuewang199511/GatherYourDeals-SDK.git
cd GatherYourDeals-SDK

# Option 1: install into your current environment (conda, venv, etc.)
pip install -e .

# Option 2: install via Poetry (uses its own virtualenv)
poetry install
```

## Quick Start

```python
from gather_your_deals import GYDClient

client = GYDClient("http://localhost:8080/api/v1")
client.users.register("alice", "password123")
client.login("alice", "password123")

receipt = client.receipts.create(
    product_name="Milk 2%",
    purchase_date="2025.04.05",
    price="5.49CAD",
    amount="2lb",
    store_name="Costco",
)

for r in client.receipts.list():
    print(r.product_name, r.price)
```

```bash
# If installed via poetry, prefix with: poetry run
gatherYourDeals login -u alice -p password123
gatherYourDeals receipts list
```

## Documentation

Full documentation is built with Sphinx:

```bash
cd docs && poetry run make html
```

The docs cover:

- **[Installation](docs/installation.rst)** — requirements, from-source install, dev extras
- **[Quick Start](docs/quickstart.rst)** — Python and CLI walkthroughs
- **[Token Storage](docs/token_storage.rst)** — where and how tokens are persisted
- **[Lazy Login](docs/lazy_login.rst)** — how automatic token refresh works
- **[Error Handling](docs/error_handling.rst)** — exception hierarchy and usage patterns
- **[API Reference](docs/api.rst)** — auto-generated from docstrings

## Development

Install in editable (development) mode with all dev dependencies:

```bash
poetry install --with dev
```

Poetry installs the package in editable mode by default, so the `gatherYourDeals` CLI and all library imports always reflect your latest code changes — no reinstall needed.

This pulls in pytest, pytest-cov, responses, ruff, mypy, sphinx, and related tooling.

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=gather_your_deals --cov-report=term-missing

# Linting
poetry run ruff check .

# Type checking
poetry run mypy gather_your_deals

# Build docs
cd docs && poetry run make html
```

## License

MIT
