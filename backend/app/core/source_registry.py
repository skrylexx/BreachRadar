"""
breachradar/config/source_registry.py

Registry of available sources — manages availability based on API keys.

This module is the central point of truth for knowing which sources
can be activated at launch time. It reads sources.yaml and
cross-references with environment variables to produce the list of
effectively active sources.

Availability rules:
1. If `enabled: false` in sources.yaml → always ignored
2. If `requires_api_key: true` AND key missing from .env → ignored + warning
3. If `requires_api_key: false` → always available (e.g. GitHub without token,
   RansomLook in Docker, RSS)
4. RansomLook is a special case: without a Docker instance, it degrades gracefully
   without a fatal error

No exception is raised if a source is missing — the scan continues
with the available sources and the report indicates the ignored sources.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_SOURCES_YAML = Path(__file__).parent / "sources.yaml"


@dataclass
class SourceStatus:
    """State of a source at launch time."""

    name: str
    enabled_in_config: bool  # enabled: true/false in sources.yaml
    requires_api_key: bool
    env_key: str | None  # Expected env variable
    api_key_present: bool  # Key found in the environment
    available: bool  # Will it actually be used?
    skip_reason: str | None = None  # Reason for exclusion (if available=False)
    description: str = ""
    config: dict = field(default_factory=dict)  # Additional config data (e.g. RSS feeds)

    @property
    def icon(self) -> str:
        if self.available:
            return "✅"
        if not self.enabled_in_config:
            return "⬜"  # Intentionally disabled
        return "⚠️ " if self.requires_api_key else "❌"


@dataclass
class SourceRegistry:
    """
    Complete registry of the state of all sources.

    Usage:
        registry = SourceRegistry.load()
        active = registry.active_sources
        registry.print_status()
    """

    sources: dict[str, SourceStatus] = field(default_factory=dict)

    @classmethod
    def load(cls, env_override: dict[str, str] | None = None) -> SourceRegistry:
        """
        Loads sources.yaml and cross-references with the current environment.

        Args:
            env_override: Optional env variables (useful for tests)
        """
        env = env_override or dict(os.environ)

        try:
            with _SOURCES_YAML.open(encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"sources.yaml introuvable : {_SOURCES_YAML}")
            return cls()

        registry = cls()
        raw_sources = config.get("sources", {})

        for source_name, source_cfg in raw_sources.items():
            enabled = source_cfg.get("enabled", False)
            requires_key = source_cfg.get("requires_api_key", False)
            env_key = source_cfg.get("env_key")
            description = source_cfg.get("description", "")

            # Capture all other keys as generic configuration
            config_data = {
                k: v
                for k, v in source_cfg.items()
                if k not in ["enabled", "requires_api_key", "env_key", "description"]
            }

            # Verify if the API key is present in the environment
            api_key_present = False
            if env_key:
                key_value = env.get(env_key, "").strip()
                # Special case Dehashed: requires DEHASHED_EMAIL + DEHASHED_API_KEY
                if source_name == "dehashed":
                    api_key_present = bool(
                        env.get("DEHASHED_EMAIL", "").strip() and env.get("DEHASHED_API_KEY", "").strip()
                    )
                # Special case Telegram: requires API_ID + API_HASH
                elif source_name == "telegram":
                    api_key_present = bool(
                        env.get("TELEGRAM_API_ID", "0").strip() not in ("", "0")
                        and env.get("TELEGRAM_API_HASH", "").strip()
                    )
                else:
                    api_key_present = bool(key_value)
            else:
                # No key required (e.g. RSS, GitHub without token)
                api_key_present = True

            # Calculate effective availability
            available, skip_reason = cls._compute_availability(
                source_name=source_name,
                enabled=enabled,
                requires_key=requires_key,
                api_key_present=api_key_present,
                env_key=env_key,
            )

            registry.sources[source_name] = SourceStatus(
                name=source_name,
                enabled_in_config=enabled,
                requires_api_key=requires_key,
                env_key=env_key,
                api_key_present=api_key_present,
                available=available,
                skip_reason=skip_reason,
                description=str(description).strip(),
                config=config_data,
            )

        registry._log_summary()
        return registry

    @staticmethod
    def _compute_availability(
        source_name: str,
        enabled: bool,
        requires_key: bool,
        api_key_present: bool,
        env_key: str | None,
    ) -> tuple[bool, str | None]:
        """
        Determines if a source is usable.

        Returns:
            (available, skip_reason) — skip_reason is None if available=True
        """
        if not enabled:
            return False, "Désactivée dans sources.yaml (enabled: false)"

        if requires_key and not api_key_present:
            key_display = env_key or "clé inconnue"
            return (
                False,
                f"Clé API manquante dans .env ({key_display}=<votre_clé>)",
            )

        return True, None

    @property
    def active_sources(self) -> list[str]:
        """List of effectively available source names."""
        return [name for name, s in self.sources.items() if s.available]

    @property
    def skipped_sources(self) -> dict[str, str]:
        """Dict source_name → exclusion reason for ignored sources."""
        return {name: (s.skip_reason or "") for name, s in self.sources.items() if not s.available}

    @property
    def missing_api_keys(self) -> list[tuple[str, str]]:
        """
        List of sources enabled in sources.yaml but missing an API key.
        Returns [(source_name, env_key), ...] — useful to guide the user.
        """
        return [
            (name, s.env_key or "")
            for name, s in self.sources.items()
            if s.enabled_in_config and s.requires_api_key and not s.api_key_present
        ]

    def is_available(self, source_name: str) -> bool:
        """Verifies if a specific source is available."""
        return self.sources.get(
            source_name,
            SourceStatus(
                name=source_name,
                enabled_in_config=False,
                requires_api_key=False,
                env_key=None,
                api_key_present=False,
                available=False,
            ),
        ).available

    def _log_summary(self) -> None:
        """Logs a summary of the sources' state at startup."""
        active = self.active_sources
        skipped = self.skipped_sources

        logger.info(f"Sources disponibles : {len(active)}/{len(self.sources)} — actives: {active}")

        for source_name, reason in skipped.items():
            status = self.sources[source_name]
            if status.enabled_in_config and status.requires_api_key and not status.api_key_present:
                # Source desired but key missing → visible warning
                logger.warning(f"Source '{source_name}' ignorée — {reason}")
            else:
                # Source intentionally disabled → debug only
                logger.debug(f"Source '{source_name}' ignorée — {reason}")

    def format_status_table(self) -> str:
        """
        Returns a text table of the state of all sources.
        Used by the CLI command `breachradar sources --status`.
        """
        lines = [
            "┌─────────────────────┬──────────┬─────────────────────────────────────────────────┐",
            "│ Source              │ Statut   │ Détail                                          │",
            "├─────────────────────┼──────────┼─────────────────────────────────────────────────┤",
        ]

        for name, status in self.sources.items():
            icon = status.icon
            state = "ACTIVE  " if status.available else ("IGNORÉE " if not status.enabled_in_config else "MANQUANT")
            detail = status.skip_reason or status.description[:46] or ""
            detail = detail[:46]  # Truncate for display

            lines.append(f"│ {name:<19} │ {icon} {state:<6} │ {detail:<47} │")

        lines.append("└─────────────────────┴──────────┴─────────────────────────────────────────────────┘")

        if self.missing_api_keys:
            lines.append("\n⚠️  Clés API manquantes (sources activées dans sources.yaml mais sans clé) :")
            for source_name, env_key in self.missing_api_keys:
                lines.append(f"   • {env_key}=<votre_clé>  → active '{source_name}'")
            lines.append("\n   Ajouter ces clés dans .env pour activer ces sources.")

        return "\n".join(lines)
