"""
tests/test_source_registry.py

Tests unitaires du SourceRegistry — disponibilité des sources selon les clés API.
"""

from __future__ import annotations

import pytest

from breachradar.config.source_registry import SourceRegistry


class TestSourceRegistryAvailability:
    """Tests de disponibilité des sources selon l'environnement."""

    def test_ransomlook_always_available(self) -> None:
        """RansomLook ne nécessite pas de clé API → toujours disponible si activé."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("ransomlook") is True

    def test_rss_always_available(self) -> None:
        """RSS ne nécessite pas de clé API → toujours disponible si activé."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("rss") is True

    def test_hibp_unavailable_without_key(self) -> None:
        """HIBP nécessite une clé → indisponible si absente."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("hibp") is False

    def test_hibp_available_with_key(self) -> None:
        """HIBP disponible si la clé API est fournie."""
        env = {"TARGET_DOMAIN": "test.fr", "HIBP_API_KEY": "test-key-abc"}
        registry = SourceRegistry.load(env_override=env)
        assert registry.is_available("hibp") is True

    def test_urlscan_unavailable_without_key(self) -> None:
        """URLScan nécessite une clé."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        assert registry.is_available("urlscan") is False

    def test_urlscan_available_with_key(self) -> None:
        env = {"TARGET_DOMAIN": "test.fr", "URLSCAN_API_KEY": "key-123"}
        registry = SourceRegistry.load(env_override=env)
        assert registry.is_available("urlscan") is True

    def test_dehashed_needs_both_credentials(self) -> None:
        """Dehashed requiert email ET api_key — email seul ne suffit pas."""
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
        # dehashed est disabled par défaut dans sources.yaml
        # Ce test vérifie le mécanisme de credential check, pas l'activation
        status = registry.sources.get("dehashed")
        assert status is not None
        assert status.api_key_present is True

    def test_disabled_source_never_available(self) -> None:
        """Une source disabled:false dans sources.yaml n'est jamais disponible,
        même si la clé est présente."""
        env = {
            "TARGET_DOMAIN": "test.fr",
            "DEHASHED_EMAIL": "me@test.fr",
            "DEHASHED_API_KEY": "key-abc",
        }
        registry = SourceRegistry.load(env_override=env)
        # dehashed est disabled par défaut
        assert registry.is_available("dehashed") is False

    def test_telegram_needs_both_id_and_hash(self) -> None:
        """Telegram nécessite API_ID ET API_HASH."""
        env_id_only = {"TARGET_DOMAIN": "test.fr", "TELEGRAM_API_ID": "12345678"}
        registry = SourceRegistry.load(env_override=env_id_only)
        status = registry.sources.get("telegram")
        assert status is not None
        assert status.api_key_present is False

    def test_empty_env_has_no_api_sources(self) -> None:
        """Sans aucune clé API, seules les sources sans clé sont actives."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        active = registry.active_sources
        # GitHub fonctionne sans token (mode anonyme)
        # RansomLook et RSS ne nécessitent pas de clé
        for source in active:
            status = registry.sources[source]
            assert not status.requires_api_key or source == "github", (
                f"Source '{source}' nécessite une clé mais est marquée active "
                "sans clé dans l'environnement"
            )

    def test_missing_api_keys_reported(self) -> None:
        """Les sources activées sans clé sont reportées dans missing_api_keys."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        missing = registry.missing_api_keys
        # HIBP est enabled:true dans sources.yaml mais nécessite une clé
        hibp_missing = any(name == "hibp" for name, _ in missing)
        assert hibp_missing is True

    def test_format_status_table_no_crash(self) -> None:
        """format_status_table() ne doit pas lever d'exception."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        table = registry.format_status_table()
        assert isinstance(table, str)
        assert len(table) > 0

    def test_active_sources_is_subset_of_all_sources(self) -> None:
        """Les sources actives sont toujours un sous-ensemble de toutes les sources."""
        registry = SourceRegistry.load(env_override={"TARGET_DOMAIN": "test.fr"})
        active = set(registry.active_sources)
        all_sources = set(registry.sources.keys())
        assert active.issubset(all_sources)
