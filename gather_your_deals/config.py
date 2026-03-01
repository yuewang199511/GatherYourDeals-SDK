"""Configuration management for the GatherYourDeals SDK.

Reads and writes settings from ``~/.GYD_SDK/env.yaml``.
"""

from pathlib import Path
from typing import Any

import yaml

from gather_your_deals.exceptions import ConfigError

_DEFAULT_DIR = Path.home() / ".GYD_SDK"
_DEFAULT_FILE = _DEFAULT_DIR / "env.yaml"

_DEFAULTS: dict[str, Any] = {
    "base_url": "http://localhost:8080/api/v1",
    "timeout": 30,
}


def _ensure_dir() -> None:
    _DEFAULT_DIR.mkdir(parents=True, exist_ok=True)


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load SDK configuration from disk.

    :param path: Override the default config path for testing.
    :returns: Merged configuration dict (defaults + file values).
    :raises ConfigError: If the file exists but cannot be parsed.
    """
    cfg_path = path or _DEFAULT_FILE
    config = dict(_DEFAULTS)
    if cfg_path.exists():
        try:
            with open(cfg_path) as f:
                data = yaml.safe_load(f) or {}
            config.update(data)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse config file {cfg_path}: {exc}") from exc
    return config


def save_config(config: dict[str, Any], path: Path | None = None) -> None:
    """Persist configuration to disk.

    Only keys that differ from the built-in defaults are written,
    plus any token or extra keys the caller provides.

    :param config: Full configuration dict.
    :param path: Override the default config path for testing.
    """
    cfg_path = path or _DEFAULT_FILE
    _ensure_dir()
    with open(cfg_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def get_token(path: Path | None = None) -> str | None:
    """Read the stored access token.

    :returns: The token string, or ``None`` if not set.
    """
    return load_config(path).get("token")


def get_refresh_token(path: Path | None = None) -> str | None:
    """Read the stored refresh token.

    :returns: The refresh token string, or ``None`` if not set.
    """
    return load_config(path).get("refresh_token")


def save_tokens(
    access_token: str,
    refresh_token: str,
    path: Path | None = None,
) -> None:
    """Store both tokens to the config file.

    :param access_token: JWT access token.
    :param refresh_token: Refresh token for obtaining new access tokens.
    """
    config = load_config(path)
    config["token"] = access_token
    config["refresh_token"] = refresh_token
    save_config(config, path)


def clear_tokens(path: Path | None = None) -> None:
    """Remove stored tokens from the config file."""
    config = load_config(path)
    config.pop("token", None)
    config.pop("refresh_token", None)
    save_config(config, path)
