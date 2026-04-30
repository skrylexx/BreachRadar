"""
leakmonitor/config/settings.py

Configuration centralisée via Pydantic Settings.
Lecture du fichier .env avec validation des types et des valeurs.

Toutes les clés API sont optionnelles (les sources sont ignorées si non configurées),
à l'exception de TARGET_DOMAIN qui est obligatoire.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration principale de LeakMonitor.
    Chargée depuis le fichier .env via python-dotenv.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignorer les variables inconnues dans .env
    )

    # ─── Domaine cible ────────────────────────────────────────────────────────
    target_domain: str = Field(
        description="Domaine à surveiller — doit vous appartenir",
    )

    # ─── Clés API — Sources gratuites ────────────────────────────────────────
    hibp_api_key: str = Field(default="", description="HaveIBeenPwned API key")
    github_token: str = Field(default="", description="GitHub Personal Access Token")
    gitlab_token: str = Field(default="", description="GitLab Personal Access Token")
    urlscan_api_key: str = Field(default="", description="URLScan.io API key")
    otx_api_key: str = Field(default="", description="AlienVault OTX API key")

    # ─── Clés API — Sources payantes ─────────────────────────────────────────
    leakcheck_api_key: str = Field(default="", description="LeakCheck.io API key")
    dehashed_email: str = Field(default="", description="Email du compte Dehashed")
    dehashed_api_key: str = Field(default="", description="Dehashed API key")
    intelx_api_key: str = Field(default="", description="Intelligence X API key")
    shodan_api_key: str = Field(default="", description="Shodan API key")

    # ─── Telegram ────────────────────────────────────────────────────────────
    telegram_api_id: int = Field(default=0, description="Telegram API ID")
    telegram_api_hash: str = Field(default="", description="Telegram API hash")

    # ─── RansomLook ──────────────────────────────────────────────────────────
    ransomlook_url: str = Field(
        default="http://localhost:8888",
        description="URL de l'instance RansomLook Docker locale",
    )
    ransomlook_search_terms: list[str] = Field(
        default_factory=list,
        description="Termes de recherche supplémentaires (noms commerciaux, filiales)",
    )
    ransomlook_alert_email: str = Field(
        default="",
        description="Email d'alerte immédiate si le domaine est détecté sur RansomLook",
    )
    ransomlook_alert_webhook: str = Field(
        default="",
        description="Webhook URL pour alerte immédiate RansomLook",
    )

    # ─── Rapports ────────────────────────────────────────────────────────────
    report_output_dir: str = Field(default="./reports")
    report_format: list[str] = Field(
        default_factory=lambda: ["markdown", "json"],
        description="Formats de rapport : markdown, json, html, pdf",
    )

    # ─── Scheduling ──────────────────────────────────────────────────────────
    schedule_enabled: bool = Field(default=False)
    schedule_cron: str = Field(
        default="0 8 * * 1",
        description="Expression cron (défaut: tous les lundis à 8h)",
    )

    # ─── Proxy ───────────────────────────────────────────────────────────────
    http_proxy: str = Field(default="")
    https_proxy: str = Field(default="")

    # ─── Logging ─────────────────────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    # ─── Timeouts ────────────────────────────────────────────────────────────
    request_timeout_seconds: int = Field(default=30)
    hibp_rate_limit_ms: int = Field(
        default=1500,
        description="Délai entre requêtes HIBP en millisecondes (respecter le rate limit)",
    )

    # ─── Validators ──────────────────────────────────────────────────────────
    @field_validator("target_domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validation basique du format de domaine."""
        v = v.strip().lower()
        if not v:
            raise ValueError("TARGET_DOMAIN est obligatoire")
        if " " in v:
            raise ValueError(f"Le domaine ne doit pas contenir d'espaces : {v}")
        if "." not in v:
            raise ValueError(f"Format de domaine invalide : {v}")
        # Supprimer le préfixe @ si présent (erreur de configuration courante)
        return v.lstrip("@")

    @field_validator("ransomlook_search_terms", mode="before")
    @classmethod
    def parse_search_terms(cls, v: str | list[str]) -> list[str]:
        """Parse la liste de termes depuis une chaîne CSV ou une liste."""
        if isinstance(v, str):
            return [term.strip() for term in v.split(",") if term.strip()]
        return v

    @field_validator("report_format", mode="before")
    @classmethod
    def parse_report_format(cls, v: str | list[str]) -> list[str]:
        """Parse les formats de rapport depuis une chaîne CSV."""
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(",") if fmt.strip()]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in valid:
            raise ValueError(f"LOG_LEVEL invalide : {v}. Valeurs acceptées : {valid}")
        return v

    # ─── Propriétés calculées ────────────────────────────────────────────────
    @property
    def all_ransomlook_terms(self) -> list[str]:
        """Retourne tous les termes de recherche RansomLook (domaine + termes configurés)."""
        terms = set(self.ransomlook_search_terms)
        terms.add(self.target_domain)
        # Ajouter aussi le domaine sans le TLD (ex: "mondomaine" pour "mondomaine.fr")
        domain_base = self.target_domain.rsplit(".", 1)[0]
        if domain_base and len(domain_base) > 3:  # Éviter les TLD courts comme "ai", "io"
            terms.add(domain_base)
        return sorted(terms)

    @property
    def hibp_configured(self) -> bool:
        return bool(self.hibp_api_key)

    @property
    def github_configured(self) -> bool:
        return bool(self.github_token)

    @property
    def leakcheck_configured(self) -> bool:
        return bool(self.leakcheck_api_key)

    @property
    def dehashed_configured(self) -> bool:
        return bool(self.dehashed_email and self.dehashed_api_key)

    @property
    def intelx_configured(self) -> bool:
        return bool(self.intelx_api_key)

    @property
    def shodan_configured(self) -> bool:
        return bool(self.shodan_api_key)

    @property
    def urlscan_configured(self) -> bool:
        return bool(self.urlscan_api_key)

    @property
    def otx_configured(self) -> bool:
        return bool(self.otx_api_key)

    @property
    def gitlab_configured(self) -> bool:
        return bool(self.gitlab_token)

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_api_id and self.telegram_api_hash)

    @property
    def ransomlook_alert_configured(self) -> bool:
        return bool(self.ransomlook_alert_email or self.ransomlook_alert_webhook)

    def get_configured_sources(self) -> list[str]:
        """
        Retourne la liste des sources qui ont leurs credentials configurés.
        RansomLook est toujours inclus (pas de clé — instance Docker locale).
        GitHub est inclus même sans token (mode anonyme, 60 req/h).
        RSS est toujours inclus (pas de clé requise).
        """
        available = ["ransomlook", "rss"]  # Toujours disponibles
        if self.hibp_configured:
            available.append("hibp")
        if self.github_configured or True:  # GitHub fonctionne sans token
            available.append("github")
        if self.gitlab_configured:
            available.append("gitlab")
        if self.urlscan_configured:
            available.append("urlscan")
        if self.otx_configured:
            available.append("otx")
        if self.leakcheck_configured:
            available.append("leakcheck")
        if self.dehashed_configured:
            available.append("dehashed")
        if self.intelx_configured:
            available.append("intelx")
        if self.shodan_configured:
            available.append("shodan")
        if self.telegram_configured:
            available.append("telegram")
        return available


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retourne l'instance singleton des settings.
    Utiliser cette fonction plutôt que d'instancier Settings directement.

    Usage :
        from leakmonitor.config.settings import get_settings
        settings = get_settings()
    """
    return Settings()


# Alias pour un import plus court
settings = get_settings()
