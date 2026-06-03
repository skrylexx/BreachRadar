"""
breachradar/models/report.py

Modèles Pydantic pour le rapport final.

Structure du rapport :
- ReportMetadata : informations sur l'exécution du scan
- SeverityBreakdown : répartition des findings par niveau
- DataIntegrity : attestation de conformité RGPD
- FinalReport : rapport complet agrégé
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.models.finding import EmailFindingResult, Severity
from app.models.ransom import RansomFinding, RansomStats


class RansomLookInstanceInfo(BaseModel):
    """Informations sur l'instance RansomLook utilisée lors du scan."""

    url: str
    is_healthy: bool
    groups_tracked: int = 0
    total_posts_indexed: int = 0
    last_update: datetime | None = None


class ReportMetadata(BaseModel):
    """Métadonnées d'exécution du scan."""

    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    target_domain: str
    sources_queried: list[str] = Field(default_factory=list)
    sources_errors: dict[str, str] = Field(
        default_factory=dict,
        description="Source → message d'erreur si applicable",
    )
    scan_duration_seconds: float = 0.0
    total_emails_checked: int = 0
    total_findings: int = 0
    ransomlook_instance: RansomLookInstanceInfo | None = None


class SeverityBreakdown(BaseModel):
    """Répartition des findings par niveau de sévérité."""

    CRITICAL: int = 0
    HIGH: int = 0
    MEDIUM: int = 0
    LOW: int = 0

    def total(self) -> int:
        return self.CRITICAL + self.HIGH + self.MEDIUM + self.LOW


class ReportSummary(BaseModel):
    """Résumé global du rapport."""

    global_severity: Severity | None = None
    ransomware_detected: bool = False
    emails_compromised: int = 0
    emails_clean: int = 0
    severity_breakdown: SeverityBreakdown = Field(default_factory=SeverityBreakdown)
    most_common_breaches: list[str] = Field(default_factory=list)
    oldest_breach: str | None = None
    newest_breach: str | None = None


class RansomwareAlerts(BaseModel):
    """Section dédiée aux alertes ransomware dans le rapport."""

    domain_listed: bool = False
    alert_count: int = 0
    alerts: list[RansomFinding] = Field(default_factory=list)


class DataIntegrity(BaseModel):
    """
    Attestation de conformité RGPD et sécurité des données.
    Incluse dans chaque rapport pour garantir la traçabilité.
    """

    no_plaintext_passwords_stored: bool = True
    no_hashes_stored: bool = True
    sanitizer_applied: bool = True
    data_purged_after_report: bool = True
    ransomlook_data_is_public: bool = True
    onion_urls_excluded_from_report: bool = True


class FinalReport(BaseModel):
    """
    Rapport final complet — structure principale du livrable.

    Format de sortie : JSON + Markdown (+ HTML et PDF optionnels).
    Ce modèle est sérialisé par le ReportEngine via les templates Jinja2.
    """

    report_metadata: ReportMetadata
    ransomware_alerts: RansomwareAlerts = Field(
        default_factory=RansomwareAlerts,
        description="Section ransomware — affichée EN TÊTE si des alertes existent",
    )
    summary: ReportSummary = Field(default_factory=ReportSummary)
    findings: list[EmailFindingResult] = Field(
        default_factory=list,
        description="Résultats par email — seuls les emails compromis sont détaillés",
    )
    ransomlook_stats: RansomStats | None = None
    data_integrity: DataIntegrity = Field(default_factory=DataIntegrity)

    def has_critical_alert(self) -> bool:
        """True si une alerte ransomware est présente — action immédiate requise."""
        return self.ransomware_alerts.domain_listed

    def get_global_severity_label(self) -> str:
        """Retourne un label emoji pour l'affichage console."""
        if self.has_critical_alert():
            return "🔴 CRITICAL (Ransomware détecté)"
        labels = {
            Severity.CRITICAL: "🔴 CRITICAL",
            Severity.HIGH: "🟠 HIGH",
            Severity.MEDIUM: "🟡 MEDIUM",
            Severity.LOW: "🟢 LOW",
        }
        if not self.summary.global_severity:
            return "✅ Aucune fuite détectée"
        return labels.get(self.summary.global_severity, "✅ Aucune fuite détectée")
