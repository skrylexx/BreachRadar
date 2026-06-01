"""
BreachRadar WebUI — Configuration (Pydantic Settings)
======================================================
Toutes les variables d'environnement validées et typées.
Fusionne la config de la WebUI et l'ancienne config du CLI.
"""

import os
from functools import lru_cache
from typing import Any, Literal

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration principale de l'API WebUI et du moteur BreachRadar."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────────────────
    environment: str = "production"  # "development" | "production"
    app_name: str = "BreachRadar WebUI"

    # ─── Base de données ─────────────────────────────────────────────────────
    database_url: str  # postgresql+asyncpg://user:pass@host:5432/dbname

    # ─── Redis ───────────────────────────────────────────────────────────────
    redis_url: str  # redis://:password@host:6379/0

    # ─── JWT ─────────────────────────────────────────────────────────────────
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # ─── Chiffrement (Clés API, SMTP) ────────────────────────────────────────
    encryption_key: str = Field(
        default="",
        description="Clé Fernet pour le chiffrement des secrets en base (doit être 32 bytes base64)",
    )

    # ─── Admin initial ────────────────────────────────────────────────────────
    initial_admin_email: EmailStr
    initial_admin_password: str

    # ─── CORS & Sécurité ─────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "breachradar-ui"]

    # ─── Politique mot de passe ───────────────────────────────────────────────
    password_min_length_admin: int = 16
    password_min_length_viewer: int = 12
    password_rotation_days: int = 180
    password_rotation_exemption_length: int = 24

    # ─── Rate limiting ────────────────────────────────────────────────────────
    rate_limit_login: str = "10/minute"
    rate_limit_scan_trigger: str = "5/minute"

    # ─── Moteur BreachRadar : Domaine cible ──────────────────────────────────
    target_domain: str = Field(
        default="example.com",
        description="Domaine à surveiller — doit vous appartenir",
    )

    # ─── Moteur BreachRadar : Clés API — Sources gratuites ───────────────────
    hibp_api_key: str = Field(default="", description="HaveIBeenPwned API key")
    github_token: str = Field(default="", description="GitHub Personal Access Token")
    gitlab_token: str = Field(default="", description="GitLab Personal Access Token")
    urlscan_api_key: str = Field(default="", description="URLScan.io API key")
    otx_api_key: str = Field(default="", description="AlienVault OTX API key")

    # ─── Moteur BreachRadar : Clés API — Sources payantes ────────────────────
    leakcheck_api_key: str = Field(default="", description="LeakCheck.io API key")
    dehashed_email: str = Field(default="", description="Email du compte Dehashed")
    dehashed_api_key: str = Field(default="", description="Dehashed API key")
    intelx_api_key: str = Field(default="", description="Intelligence X API key")
    shodan_api_key: str = Field(default="", description="Shodan API key")
    hunter_api_key: str = Field(
        default="", description="Hunter.io API key pour le résolveur d'emails"
    )

    # ─── Telegram ────────────────────────────────────────────────────────────
    telegram_api_id: int = Field(default=0, description="Telegram API ID")
    telegram_api_hash: str = Field(default="", description="Telegram API hash")

    # ─── RansomLook ──────────────────────────────────────────────────────────
    ransomlook_mode: Literal["local", "saas"] = Field(
        default="local",
        description="Mode d'utilisation de RansomLook : instance Docker locale ou API SaaS",
    )
    ransomlook_local_url: str = Field(
        default="http://ransomlook-app:8888",
        description="URL de l'instance RansomLook Docker locale",
    )
    ransomlook_saas_api_url: str = Field(
        default="https://www.ransomlook.io/api",
        description="URL de l'API SaaS RansomLook (hébergée)",
    )
    ransomlook_saas_api_key: str = Field(
        default="",
        description="Clé d'API pour l'instance SaaS RansomLook (header Authorization)",
    )
    ransomlook_search_terms: str | list[str] = Field(
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

    # ─── SMTP (notifications + reset password) ───────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_tls: bool = True

    # ─── Rapports ────────────────────────────────────────────────────────────
    report_output_dir: str = Field(default="./reports")
    report_format: str | list[str] = Field(
        default_factory=lambda: ["markdown", "json"],
        description="Formats de rapport : markdown, json, html, pdf",
    )

    # ─── Scheduling ──────────────────────────────────────────────────────────
    schedule_enabled: bool = Field(default=False)
    schedule_cron: str = Field(
        default="0 8 * * 1",
        description="Expression cron (défaut: tous les lundis à 8h)",
    )
    cve_polling_interval: int = Field(
        default=60,
        description="Intervalle de polling CVE en minutes (défaut: 60)",
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

    # ─── Veille CVE (NVD API 2.0) ────────────────────────────────────────────
    cve_nvd_api_key: str = Field(
        default="",
        description=(
            "Clé API optionnelle pour le NVD (NIST). "
            "Sans clé : 5 req/30s. Avec clé : 50 req/30s. "
            "https://nvd.nist.gov/developers/request-an-api-key"
        ),
    )

    # ─── Validators ──────────────────────────────────────────────────────────
    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("initial_admin_email", mode="before")
    @classmethod
    def fallback_initial_admin_email(cls, v: str | None) -> str:
        """Permet d'utiliser UI_ADMIN_EMAIL si INITIAL_ADMIN_EMAIL n'est pas défini."""
        if v:
            return v
        env_val = os.getenv("UI_ADMIN_EMAIL")
        if env_val:
            return env_val
        raise ValueError("INITIAL_ADMIN_EMAIL must be set (or UI_ADMIN_EMAIL)")

    @field_validator("initial_admin_password", mode="before")
    @classmethod
    def fallback_initial_admin_password(cls, v: str | None) -> str:
        """Permet d'utiliser UI_ADMIN_PASSWORD si INITIAL_ADMIN_PASSWORD n'est pas défini."""
        if v:
            return v
        env_val = os.getenv("UI_ADMIN_PASSWORD")
        if env_val:
            return env_val
        raise ValueError("INITIAL_ADMIN_PASSWORD must be set (or UI_ADMIN_PASSWORD)")

    @field_validator("initial_admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("INITIAL_ADMIN_PASSWORD must be at least 16 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("INITIAL_ADMIN_PASSWORD must not exceed 72 bytes (bcrypt limit)")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:3000", "http://127.0.0.1:3000"]
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                # Fallback to comma separated
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("ransomlook_search_terms", mode="before")
    @classmethod
    def parse_search_terms(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [term.strip() for term in v.split(",") if term.strip()]
        return v

    @field_validator("report_format", mode="before")
    @classmethod
    def parse_report_format(cls, v: str | list[str]) -> list[str]:
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
        terms = set(self.ransomlook_search_terms)
        terms.add(self.target_domain)
        domain_base = self.target_domain.rsplit(".", 1)[0]
        if domain_base and len(domain_base) > 3:
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
    def hunter_configured(self) -> bool:
        return bool(self.hunter_api_key)

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

    @property
    def nvd_configured(self) -> bool:
        """True si une clé NVD est présente (rate-limit étendu : 50 req/30s)."""
        return bool(self.cve_nvd_api_key)

    def get_configured_sources(self) -> list[str]:
        available = ["ransomlook", "rss"]
        if self.hibp_configured:
            available.append("hibp")
        if True:
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


@lru_cache
def get_settings() -> Settings:
    """Singleton des settings (caché après le premier appel)."""
    return Settings()  # type: ignore[call-arg]


settings: Settings = get_settings()
