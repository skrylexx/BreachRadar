"""
tests/test_source_registry.py

Unit tests for the SourceRegistry — availability of sources according to API keys.
"""

from __future__ import annotations

from app.core.source_registry import SourceRegistry


class TestSourceRegistryAvailability:
    """Tests of source availability according to the environment."""

    def test_ransomlook_always_available(self) -> None:
        """RansomLook does not require an API key → always available if enabled."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("ransomlook") is True

    def test_rss_always_available(self) -> None:
        """RSS does not require an API key → always available if enabled."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("rss") is True

    def test_hibp_unavailable_without_key(self) -> None:
        """HIBP requires a key → unavailable if absent."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("hibp") is False

    def test_hibp_available_with_key(self) -> None:
        """HIBP available if the API key is provided."""
        env = {"TARGET_DOMAIN": "test.fr", "HIBP_API_KEY": "test-key-abc"}
        registry = SourceRegistry.load(env_override=env)
        assert registry.is_available("hibp") is True

    def test_urlscan_unavailable_without_key(self) -> None:
        """URLScan requires a key."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("urlscan") is False

    def test_urlscan_available_with_key(self) -> None:
        env = {"TARGET_DOMAIN": "test.fr", "URLSCAN_API_KEY": "key-123"}
        registry = SourceRegistry.load(env_override=env)
        assert registry.is_available("urlscan") is True

    def test_dehashed_needs_both_credentials(self) -> None:
        """Dehashed requires email AND api_key — email alone is not enough."""
        env_email_only = {"TARGET_DOMAIN": "test.fr", "DEHASHED_EMAIL": "me@test.fr"}
        registry = SourceRegistry.load(env_override=env_email_only)
        assert registry.is_available("dehashed") is False

    def test_dehashed_available_with_both(self) -> None:
        env = {
            "TARGET_DOMAIN": "test.fr",
            "DEHASHED_EMAIL": "me@test.fr",
            "DEHASHED_API_KEY": "key-abc",
        }
        registry = SourceRegistry.load(env_override=env)
        # dehashed is disabled by default in sources.yaml
        # This test verifies the credential check mechanism, not activation
        status = registry.sources.get("dehashed")
        assert status is not None
        assert status.api_key_present is True

    def test_disabled_source_never_available(self) -> None:
        """A source disabled:false in sources.yaml is never available,
        even if the key is present."""
        env = {
            "TARGET_DOMAIN": "test.fr",
            "DEHASHED_EMAIL": "me@test.fr",
            "DEHASHED_API_KEY": "key-abc",
        }
        registry = SourceRegistry.load(env_override=env)
        # dehashed is disabled by default
        assert registry.is_available("dehashed") is False

    def test_telegram_needs_both_id_and_hash(self) -> None:
        """Telegram requires API_ID AND API_HASH."""
        env_id_only = {"TARGET_DOMAIN": "test.fr", "TELEGRAM_API_ID": "12345678"}
        registry = SourceRegistry.load(env_override=env_id_only)
        status = registry.sources.get("telegram")
        assert status is not None
        assert status.api_key_present is False

    def test_empty_env_has_no_api_sources(self) -> None:
        """Without any API key, only sources without a key are active."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        active = registry.active_sources
        # GitHub works without a token (anonymous mode)
        # RansomLook and RSS do not require a key
        for source in active:
            status = registry.sources[source]
            assert not status.requires_api_key or source == "github", (
                f"Source '{source}' requires a key but is marked active without a key in the environment"
            )

    def test_missing_api_keys_reported(self) -> None:
        """Activated sources without a key are reported in missing_api_keys."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        missing = registry.missing_api_keys
        # HIBP is enabled:true in sources.yaml but requires a key
        hibp_missing = any(name == "hibp" for name, _ in missing)
        assert hibp_missing is True

    def test_format_status_table_no_crash(self) -> None:
        """format_status_table() must not raise an exception."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        table = registry.format_status_table()
        assert isinstance(table, str)
        assert len(table) > 0

    def test_active_sources_is_subset_of_all_sources(self) -> None:
        """Active sources are always a subset of all sources."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        active = set(registry.active_sources)
        all_sources = set(registry.sources.keys())
        assert active.issubset(all_sources)
