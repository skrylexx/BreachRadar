"""
BreachRadar WebUI — Configuration (Pydantic Settings)
======================================================
Toutes les variables d'environnement validées et typées.
"""

from functools import lru_cache
from typing import List

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration principale de l'API WebUI."""

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

    # ─── Admin initial ────────────────────────────────────────────────────────
    initial_admin_email: EmailStr
    initial_admin_password: str

    # ─── CORS & Sécurité ─────────────────────────────────────────────────────
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1", "breachradar-ui"]

    # ─── Politique mot de passe ───────────────────────────────────────────────
    # Admin : 16 chars min, Viewer : 12 chars min
    password_min_length_admin: int = 16
    password_min_length_viewer: int = 12
    # Rotation obligatoire tous les 180 jours (sauf si >24 chars)
    password_rotation_days: int = 180
    password_rotation_exemption_length: int = 24

    # ─── Rate limiting ────────────────────────────────────────────────────────
    rate_limit_login: str = "10/minute"        # Endpoint /auth/login
    rate_limit_scan_trigger: str = "5/minute"  # Endpoint /scans/trigger

    # ─── SMTP (notifications + reset password) ───────────────────────────────
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_tls: bool = True

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("initial_admin_password")
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("INITIAL_ADMIN_PASSWORD must be at least 16 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    """Singleton des settings (caché après le premier appel)."""
    return Settings()


settings: Settings = get_settings()
