"""
breachradar/config/source_registry.py

Registre des sources disponibles — gestion de la disponibilité en fonction des clés API.

Ce module est le point central de vérité pour savoir quelles sources
peuvent être activées au moment du lancement. Il lit sources.yaml et
croise avec les variables d'environnement pour produire la liste des
sources effectivement actives.

Règles de disponibilité :
1. Si `enabled: false` dans sources.yaml → toujours ignorée
2. Si `requires_api_key: true` ET clé absente du .env → ignorée + warning
3. Si `requires_api_key: false` → toujours disponible (ex: GitHub sans token,
   RansomLook en Docker, RSS)
4. RansomLook est un cas spécial : sans instance Docker, on dégrade gracieusement
   sans erreur fatale

Aucune exception n'est levée si une source est manquante — le scan continue
avec les sources disponibles et le rapport indique les sources ignorées.
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
    """État d'une source au moment du lancement."""

    name: str
    enabled_in_config: bool          # enabled: true/false dans sources.yaml
    requires_api_key: bool
    env_key: str | None              # Variable d'env attendue
    api_key_present: bool            # Clé trouvée dans l'environnement
    available: bool                  # Sera effectivement utilisée ?
    skip_reason: str | None = None   # Raison d'exclusion (si available=False)
    description: str = ""

    @property
    def icon(self) -> str:
        if self.available:
            return "✅"
        if not self.enabled_in_config:
            return "⬜"  # Désactivée volontairement
        return "⚠️ " if self.requires_api_key else "❌"


@dataclass
class SourceRegistry:
    """
    Registre complet de l'état de toutes les sources.

    Usage :
        registry = SourceRegistry.load()
        active = registry.active_sources
        registry.print_status()
    """

    sources: dict[str, SourceStatus] = field(default_factory=dict)

    @classmethod
    def load(cls, env_override: dict[str, str] | None = None) -> "SourceRegistry":
        """
        Charge sources.yaml et croise avec l'environnement courant.

        Args:
            env_override: Variables d'env optionnelles (utile pour les tests)
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

            # Vérifier si la clé API est présente dans l'environnement
            api_key_present = False
            if env_key:
                key_value = env.get(env_key, "").strip()
                # Cas spécial Dehashed : nécessite DEHASHED_EMAIL + DEHASHED_API_KEY
                if source_name == "dehashed":
                    api_key_present = bool(
                        env.get("DEHASHED_EMAIL", "").strip()
                        and env.get("DEHASHED_API_KEY", "").strip()
                    )
                # Cas spécial Telegram : nécessite API_ID + API_HASH
                elif source_name == "telegram":
                    api_key_present = bool(
                        env.get("TELEGRAM_API_ID", "0").strip() not in ("", "0")
                        and env.get("TELEGRAM_API_HASH", "").strip()
                    )
                else:
                    api_key_present = bool(key_value)
            else:
                # Pas de clé requise (ex: RSS, GitHub sans token)
                api_key_present = True

            # Calculer la disponibilité effective
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
        Détermine si une source est utilisable.

        Returns:
            (available, skip_reason) — skip_reason est None si available=True
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
        """Liste des noms de sources effectivement disponibles."""
        return [name for name, s in self.sources.items() if s.available]

    @property
    def skipped_sources(self) -> dict[str, str]:
        """Dict source_name → raison d'exclusion pour les sources ignorées."""
        return {
            name: (s.skip_reason or "")
            for name, s in self.sources.items()
            if not s.available
        }

    @property
    def missing_api_keys(self) -> list[tuple[str, str]]:
        """
        Liste des sources activées dans sources.yaml mais sans clé API.
        Retourne [(source_name, env_key), ...] — utile pour guider l'utilisateur.
        """
        return [
            (name, s.env_key or "")
            for name, s in self.sources.items()
            if s.enabled_in_config and s.requires_api_key and not s.api_key_present
        ]

    def is_available(self, source_name: str) -> bool:
        """Vérifie si une source spécifique est disponible."""
        return self.sources.get(source_name, SourceStatus(
            name=source_name, enabled_in_config=False, requires_api_key=False,
            env_key=None, api_key_present=False, available=False,
        )).available

    def _log_summary(self) -> None:
        """Log un résumé de l'état des sources au démarrage."""
        active = self.active_sources
        skipped = self.skipped_sources

        logger.info(
            f"Sources disponibles : {len(active)}/{len(self.sources)} — "
            f"actives: {active}"
        )

        for source_name, reason in skipped.items():
            status = self.sources[source_name]
            if status.enabled_in_config and status.requires_api_key and not status.api_key_present:
                # Source voulue mais clé manquante → warning visible
                logger.warning(
                    f"Source '{source_name}' ignorée — {reason}"
                )
            else:
                # Source désactivée volontairement → debug seulement
                logger.debug(f"Source '{source_name}' ignorée — {reason}")

    def format_status_table(self) -> str:
        """
        Retourne un tableau texte de l'état de toutes les sources.
        Utilisé par la commande CLI `breachradar sources --status`.
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
            detail = detail[:46]  # Tronquer pour l'affichage

            lines.append(
                f"│ {name:<19} │ {icon} {state:<6} │ {detail:<47} │"
            )

        lines.append(
            "└─────────────────────┴──────────┴─────────────────────────────────────────────────┘"
        )

        if self.missing_api_keys:
            lines.append("\n⚠️  Clés API manquantes (sources activées dans sources.yaml mais sans clé) :")
            for source_name, env_key in self.missing_api_keys:
                lines.append(f"   • {env_key}=<votre_clé>  → active '{source_name}'")
            lines.append("\n   Ajouter ces clés dans .env pour activer ces sources.")

        return "\n".join(lines)
