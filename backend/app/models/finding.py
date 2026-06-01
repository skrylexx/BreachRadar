"""
breachradar/models/finding.py

Modèles Pydantic et SQLAlchemy pour les résultats de scan et de veille.

RÈGLE DE SÉCURITÉ FONDAMENTALE :
Ce modèle ne contient AUCUN champ pour les données sensibles brutes
(passwords, hashs, tokens, clés API). La sérialisation JSON ne peut donc
pas les exposer accidentellement. Seuls des flags booléens sont stockés.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Severity(enum.StrEnum):
    """Niveau de sévérité d'un finding ou d'un rapport."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __gt__(self, other: Severity) -> bool:
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) > order.index(other)

    def __ge__(self, other: Severity) -> bool:
        return self == other or self.__gt__(other)


class CyberFinding(Base):
    """
    Modèle générique pour les trouvailles de la veille numérique (RSS, Paste, GitHub, etc.).
    """

    __tablename__ = "cyber_findings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ─── Identité & Source ──────────────────────────────────────────────────
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    finding_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "rss", "paste", "github", "leak"

    # ─── Contenu ───────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=True)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.LOW, nullable=False)

    # ─── Méta-données flexibles ─────────────────────────────────────────────
    # Permet de stocker CVE_ID, Tags, Mots-clés détectés, etc.
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ─── État ──────────────────────────────────────────────────────────────
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ─── Timestamps ────────────────────────────────────────────────────────
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LeakFinding(BaseModel):
    """
    Résultat d'une détection de fuite pour un email donné.

    IMPORTANT — Pas de données sensibles :
    Ce modèle ne stocke JAMAIS de mot de passe, hash, token ou clé API.
    Seuls des indicateurs booléens sont conservés (has_password, has_hash, etc.)
    pour permettre le calcul de sévérité sans exposer les données.
    """

    source: str = Field(description="Nom de la source (hibp, leakcheck, dehashed...)")
    email: str = Field(description="Adresse email concernée par la fuite")
    breach_name: str = Field(description="Nom de la fuite (ex: 'Adobe 2013')")
    breach_date: date | None = Field(default=None, description="Date estimée de la fuite")
    data_classes: list[str] = Field(
        default_factory=list,
        description="Types de données exposées (pas les données elles-mêmes)",
    )

    # Indicateurs booléens — JAMAIS les données elles-mêmes
    has_password: bool = Field(
        default=False,
        description="Un mot de passe était présent dans cette fuite",
    )
    has_hash: bool = Field(
        default=False,
        description="Un hash de mot de passe était présent",
    )
    has_api_key: bool = Field(
        default=False,
        description="Une clé API ou token était présent",
    )
    has_plaintext_credential: bool = Field(
        default=False,
        description="Un credential en clair a été détecté",
    )

    severity: Severity = Field(description="Niveau de sévérité calculé")
    verified: bool = Field(
        default=True,
        description="La fuite est-elle vérifiée/confirmée par la source ?",
    )
    is_sensitive: bool = Field(
        default=False,
        description="La fuite est-elle marquée comme sensible (ex: site adulte) ?",
    )
    raw_data_sanitized: bool = Field(
        default=True,
        description="Toujours True — les données brutes sont purgées avant stockage",
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validation basique du format email."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError(f"Format email invalide : {v}")
        return v.lower()


class EmailFindingResult(BaseModel):
    """
    Résultat agrégé pour une adresse email donnée.
    Combine tous les findings de toutes les sources pour cet email.
    """

    email: str
    status: str = Field(
        description="COMPROMISED si au moins un finding, CLEAN sinon",
    )
    severity: Severity | None = Field(
        default=None,
        description="Sévérité maximale parmi tous les findings de cet email",
    )
    breach_count: int = Field(default=0)
    findings: list[LeakFinding] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_compromised(self) -> bool:
        return len(self.findings) > 0

    def get_severity_label(self) -> str:
        """Retourne un label emoji pour l'affichage console."""
        labels = {
            Severity.CRITICAL: "🔴 CRITICAL",
            Severity.HIGH: "🟠 HIGH",
            Severity.MEDIUM: "🟡 MEDIUM",
            Severity.LOW: "🟢 LOW",
        }
        return labels.get(self.severity, "✅ CLEAN") if self.severity else "✅ CLEAN"
