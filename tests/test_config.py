"""Tests for configuration management."""

from pathlib import Path

from gather_your_deals.config import (
    clear_tokens,
    get_refresh_token,
    get_token,
    load_config,
    save_config,
    save_tokens,
)


class TestConfig:
    def test_load_defaults(self, tmp_path: Path):
        cfg = load_config(tmp_path / "nonexistent.yaml")
        assert cfg["base_url"] == "http://localhost:8080/api/v1"
        assert cfg["timeout"] == 30

    def test_save_and_load(self, tmp_path: Path):
        p = tmp_path / "env.yaml"
        save_config({"base_url": "http://example.com", "timeout": 10}, p)
        cfg = load_config(p)
        assert cfg["base_url"] == "http://example.com"
        assert cfg["timeout"] == 10

    def test_save_and_get_tokens(self, tmp_path: Path):
        p = tmp_path / "env.yaml"
        save_tokens("access-abc", "refresh-xyz", p)
        assert get_token(p) == "access-abc"
        assert get_refresh_token(p) == "refresh-xyz"

    def test_clear_tokens(self, tmp_path: Path):
        p = tmp_path / "env.yaml"
        save_tokens("access-abc", "refresh-xyz", p)
        clear_tokens(p)
        assert get_token(p) is None
        assert get_refresh_token(p) is None
