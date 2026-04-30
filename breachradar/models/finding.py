"""
breachradar/models/finding.py

Modèles Pydantic pour les résultats de scan email/domaine.

RÈGLE DE SÉCURITÉ FONDAMENTALE :
Ce modèle ne contient AUCUN champ pour les données sensibles brutes
(passwords, hashs, tokens, clés API). La sérialisation JSON ne peut donc
pas les exposer accidentellement. Seuls des flags booléens sont stockés.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    """Niveau de sévérité d'un finding ou d'un rapport."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __gt__(self, other: "Severity") -> bool:
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) > order.index(other)

    def __ge__(self, other: "Severity") -> bool:
        return self == other or self.__gt__(other)


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
