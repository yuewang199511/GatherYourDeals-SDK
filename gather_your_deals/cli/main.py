"""Command-line interface for the GatherYourDeals SDK.

Run ``gatherYourDeals --help`` to see available commands.
"""

from __future__ import annotations

import json
import sys

import click

from gather_your_deals.client import GYDClient
from gather_your_deals.config import load_config, save_config
from gather_your_deals.exceptions import GYDError


def _get_client() -> GYDClient:
    """Create a client using the stored configuration."""
    return GYDClient()


# ── Root group ───────────────────────────────────────────────────────────

@click.group()
@click.version_option(package_name="gather-your-deals")
def cli() -> None:
    """GatherYourDeals — manage your purchase data from the terminal."""


# ── Config ───────────────────────────────────────────────────────────────

@cli.command()
@click.argument("base_url")
def config(base_url: str) -> None:
    """Set the API base URL.

    Example: gatherYourDeals config http://localhost:8080/api/v1
    """
    cfg = load_config()
    cfg["base_url"] = base_url
    save_config(cfg)
    click.echo(f"Base URL set to {base_url}")


# ── Auth ─────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--username", "-u", prompt=True, help="Account username.")
@click.option(
    "--password", "-p", prompt=True, hide_input=True, help="Account password."
)
def login(username: str, password: str) -> None:
    """Log in and store the access token locally.

    The token is saved to ~/.GYD_SDK/env.yaml and used for
    subsequent commands. It is only verified when a request is sent.
    """
    try:
        client = _get_client()
        client.login(username, password)
        click.echo("Login successful. Token saved.")
    except GYDError as exc:
        click.echo(f"Login failed: {exc}", err=True)
        sys.exit(1)


@cli.command()
def logout() -> None:
    """Log out and clear stored tokens."""
    try:
        client = _get_client()
        client.logout()
        click.echo("Logged out. Tokens cleared.")
    except GYDError as exc:
        click.echo(f"Logout failed: {exc}", err=True)
        sys.exit(1)


@cli.command()
def me() -> None:
    """Show current authenticated user info."""
    try:
        client = _get_client()
        info = client.me()
        click.echo(json.dumps(info, indent=2))
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── User registration ───────────────────────────────────────────────────

@cli.command()
@click.option("--username", "-u", prompt=True, help="Desired username.")
@click.option(
    "--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True,
    help="Password (min 8 characters)."
)
def register(username: str, password: str) -> None:
    """Register a new user account."""
    try:
        client = _get_client()
        user = client.users.register(username, password)
        click.echo(f"User created: {user.username} (id={user.id}, role={user.role})")
    except GYDError as exc:
        click.echo(f"Registration failed: {exc}", err=True)
        sys.exit(1)


# ── Meta fields ──────────────────────────────────────────────────────────

@cli.group()
def meta() -> None:
    """Manage field definitions."""


@meta.command("list")
def meta_list() -> None:
    """List all registered fields."""
    try:
        client = _get_client()
        fields = client.meta.list()
        for f in fields:
            native = " [native]" if f.native else ""
            click.echo(f"  {f.field_name} ({f.type}): {f.description}{native}")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@meta.command("add")
@click.argument("field_name")
@click.argument("description")
@click.option("--type", "field_type", default="string", help="Field type.")
def meta_add(field_name: str, description: str, field_type: str) -> None:
    """Register a new user-defined field."""
    try:
        client = _get_client()
        f = client.meta.register(field_name, description, field_type)
        click.echo(f"Field registered: {f.field_name} ({f.type})")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── Receipts ─────────────────────────────────────────────────────────────

@cli.group()
def receipts() -> None:
    """Manage purchase records."""


@receipts.command("list")
def receipts_list() -> None:
    """List all your receipts."""
    try:
        client = _get_client()
        items = client.receipts.list()
        if not items:
            click.echo("No receipts found.")
            return
        for r in items:
            click.echo(
                f"  [{r.id[:8]}] {r.purchase_date}  {r.product_name:30s}"
                f"  {r.price:>10s}  @ {r.store_name}"
            )
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@receipts.command("get")
@click.argument("receipt_id")
def receipts_get(receipt_id: str) -> None:
    """Get a receipt by ID."""
    try:
        client = _get_client()
        r = client.receipts.get(receipt_id)
        click.echo(json.dumps(r.to_dict(), indent=2))
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@receipts.command("add")
@click.option("--product-name", "-n", required=True, help="Product name.")
@click.option("--date", "-d", required=True, help="Purchase date (Y.M.D).")
@click.option("--price", "-p", required=True, help="Price with currency.")
@click.option("--amount", "-a", required=True, help="Amount (e.g. 1 or 2lb).")
@click.option("--store", "-s", required=True, help="Store name.")
@click.option("--lat", type=float, default=None, help="Latitude.")
@click.option("--lon", type=float, default=None, help="Longitude.")
@click.option(
    "--extra", "-e", multiple=True,
    help="Extra field as key=value. Repeat for multiple."
)
def receipts_add(
    product_name: str,
    date: str,
    price: str,
    amount: str,
    store: str,
    lat: float | None,
    lon: float | None,
    extra: tuple[str, ...],
) -> None:
    """Create a new receipt."""
    extras: dict[str, str] = {}
    for pair in extra:
        if "=" not in pair:
            click.echo(f"Invalid extra format '{pair}'. Use key=value.", err=True)
            sys.exit(1)
        k, v = pair.split("=", 1)
        extras[k] = v

    try:
        client = _get_client()
        r = client.receipts.create(
            product_name=product_name,
            purchase_date=date,
            price=price,
            amount=amount,
            store_name=store,
            latitude=lat,
            longitude=lon,
            extras=extras or None,
        )
        click.echo(f"Receipt created: {r.id}")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@receipts.command("delete")
@click.argument("receipt_id")
@click.confirmation_option(prompt="Are you sure you want to delete this receipt?")
def receipts_delete(receipt_id: str) -> None:
    """Delete a receipt by ID."""
    try:
        client = _get_client()
        client.receipts.delete(receipt_id)
        click.echo(f"Receipt {receipt_id} deleted.")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


# ── Batch import ─────────────────────────────────────────────────────────

@receipts.command("import")
@click.argument("file", type=click.Path(exists=True))
def receipts_import(file: str) -> None:
    """Bulk-import receipts from a JSON file.

    The file should contain a JSON array of receipt objects.
    """
    try:
        with open(file) as f:
            records = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        click.echo(f"Failed to read {file}: {exc}", err=True)
        sys.exit(1)

    if not isinstance(records, list):
        click.echo("JSON file must contain an array of receipt objects.", err=True)
        sys.exit(1)

    client = _get_client()
    ok, fail = 0, 0
    for i, record in enumerate(records):
        try:
            from gather_your_deals.models import Receipt

            receipt = Receipt.from_dict(record)
            client.receipts.create_from_receipt(receipt)
            ok += 1
        except GYDError as exc:
            click.echo(f"  Record {i}: {exc}", err=True)
            fail += 1

    click.echo(f"Import complete: {ok} succeeded, {fail} failed.")


# ── Admin ────────────────────────────────────────────────────────────────

@cli.group()
def admin() -> None:
    """Admin-only operations."""


@admin.command("users")
def admin_list_users() -> None:
    """List all users (admin only)."""
    try:
        client = _get_client()
        users = client.admin.list_users()
        for u in users:
            click.echo(f"  {u.id}  {u.username:20s}  role={u.role}")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@admin.command("delete-user")
@click.argument("user_id")
@click.confirmation_option(prompt="Are you sure you want to delete this user?")
def admin_delete_user(user_id: str) -> None:
    """Delete a user (admin only)."""
    try:
        client = _get_client()
        client.admin.delete_user(user_id)
        click.echo(f"User {user_id} deleted.")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@admin.command("update-field")
@click.argument("field_name")
@click.argument("description")
def admin_update_field(field_name: str, description: str) -> None:
    """Update a field description (admin only)."""
    try:
        client = _get_client()
        client.admin.update_field_description(field_name, description)
        click.echo(f"Field '{field_name}' description updated.")
    except GYDError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
