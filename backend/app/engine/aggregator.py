"""
breachradar/core/aggregator.py

Déduplication et agrégation des findings.

Responsabilités :
1. Dédupliquer les findings identiques provenant de sources multiples
2. Calculer la sévérité par email (basée sur les types de données exposées)
3. Calculer la sévérité globale du rapport
4. Intégrer les RansomFindings comme signal de sévérité maximale globale

RÈGLE CRITIQUE RansomLook :
Si un RansomFinding est présent, la sévérité GLOBALE est TOUJOURS CRITICAL.
Cette règle n'est pas négociable — une compromission ransomware en cours
est le scénario le plus grave possible.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, date, datetime

from app.models.finding import (
    EmailFindingResult,
    LeakFinding,
    Severity,
)
from app.models.ransom import RansomFinding
from app.models.report import (
    FinalReport,
    RansomwareAlerts,
    ReportMetadata,
    ReportSummary,
    SeverityBreakdown,
)

logger = logging.getLogger(__name__)

# Recommandations génériques par niveau de sévérité
SEVERITY_RECOMMENDATIONS: dict[Severity, list[str]] = {
    Severity.CRITICAL: [
        "Forcer la réinitialisation du mot de passe immédiatement",
        "Activer l'authentification multi-facteurs (MFA)",
        "Révoquer toutes les sessions actives",
        "Auditer les accès récents dans les journaux",
        "Vérifier les accès aux systèmes sensibles liés à ce compte",
    ],
    Severity.HIGH: [
        "Forcer la réinitialisation du mot de passe",
        "Activer l'authentification multi-facteurs (MFA)",
        "Surveiller les connexions inhabituelles",
    ],
    Severity.MEDIUM: [
        "Envisager de changer le mot de passe par précaution",
        "Vérifier que l'authentification multi-facteurs est activée",
    ],
    Severity.LOW: [
        "Surveiller les activités inhabituelles sur ce compte",
        "S'assurer que le mot de passe n'est pas réutilisé ailleurs",
    ],
}


class ResultAggregator:
    """
    Agrège, déduplique et calcule les sévérités des findings.

    Usage :
        aggregator = ResultAggregator()
        report = aggregator.aggregate(
            email_findings=all_findings,
            ransom_findings=ransom_findings,
            metadata=metadata,
        )
    """

    def aggregate(
        self,
        email_findings: list[LeakFinding],
        ransom_findings: list[RansomFinding],
        metadata: ReportMetadata,
    ) -> FinalReport:
        """
        Point d'entrée principal — produit le FinalReport complet.

        ⚠️  RÈGLE CRITIQUE : Si ransom_findings est non vide, la sévérité
        globale est CRITICAL quelle que soit la sévérité des email_findings.

        Args:
            email_findings: Tous les findings email (toutes sources confondues)
            ransom_findings: Findings RansomLook (peut être vide)
            metadata: Métadonnées du scan

        Returns:
            FinalReport complet et prêt à être rendu
        """
        # 1. Dédupliquer et regrouper les findings par email
        email_results = self._deduplicate_and_group(email_findings)

        # 2. Calculer la sévérité de chaque email
        for result in email_results.values():
            result.severity = self._calculate_email_severity(result.findings)
            result.recommendations = SEVERITY_RECOMMENDATIONS.get(result.severity, [])

        # 3. Construire le bloc d'alertes ransomware
        ransomware_alerts = RansomwareAlerts(
            domain_listed=len(ransom_findings) > 0,
            alert_count=len(ransom_findings),
            alerts=ransom_findings,
        )

        # 4. Calculer la sévérité globale
        global_severity = self._calculate_global_severity(list(email_results.values()), ransom_findings)

        # 5. Construire le résumé
        summary = self._build_summary(list(email_results.values()), ransom_findings)
        summary.global_severity = global_severity
        summary.ransomware_detected = len(ransom_findings) > 0

        # 6. Trier les findings par sévérité (CRITICAL en premier)
        sorted_findings = sorted(
            email_results.values(),
            key=lambda r: [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW].index(
                r.severity or Severity.LOW
            ),
        )

        return FinalReport(
            report_metadata=metadata,
            ransomware_alerts=ransomware_alerts,
            summary=summary,
            findings=sorted_findings,
        )

    def _deduplicate_and_group(self, findings: list[LeakFinding]) -> dict[str, EmailFindingResult]:
        """
        Groupe les findings par email et déduplique les breaches identiques.
        Un breach est un doublon si (email, breach_name, source) est identique.

        Returns:
            Dictionnaire email → EmailFindingResult dédupliqué
        """
        grouped: dict[str, list[LeakFinding]] = defaultdict(list)
        seen_breaches: dict[str, set[tuple[str, str]]] = defaultdict(set)

        for finding in findings:
            # Clé de déduplication : (breach_name, source)
            dedup_key = (finding.breach_name.lower(), finding.source)

            if dedup_key in seen_breaches[finding.email]:
                logger.debug(
                    f"Doublon ignoré : email={finding.email}, breach={finding.breach_name}, source={finding.source}"
                )
                continue

            seen_breaches[finding.email].add(dedup_key)
            grouped[finding.email].append(finding)

        results = {}
        for email, email_findings in grouped.items():
            results[email] = EmailFindingResult(
                email=email,
                status="COMPROMISED",
                breach_count=len(email_findings),
                findings=email_findings,
                checked_at=datetime.now(UTC),
            )

        logger.info(
            f"Agrégation : {len(findings)} findings → "
            f"{sum(r.breach_count for r in results.values())} uniques "
            f"pour {len(results)} emails compromis"
        )
        return results

    def _calculate_email_severity(self, findings: list[LeakFinding]) -> Severity:
        """
        Calcule la sévérité maximale pour un email donné.

        Règles (par ordre de priorité décroissant) :
        - Credential en clair ou clé API → CRITICAL
        - Hash de mot de passe → HIGH (+ escalade si récent)
        - Données PII uniquement → MEDIUM
        - Données non-sensibles, breach ancienne → LOW

        La sévérité est escaladée d'un niveau si la breach est récente (<6 mois).
        """
        if not findings:
            return Severity.LOW

        max_severity = Severity.LOW

        for finding in findings:
            severity = self._finding_severity(finding)
            if severity > max_severity:
                max_severity = severity

        return max_severity

    def _finding_severity(self, finding: LeakFinding) -> Severity:
        """Calcule la sévérité d'un LeakFinding individuel."""
        # Credential en clair ou clé API → CRITICAL immédiat
        if finding.has_plaintext_credential or finding.has_api_key:
            return Severity.CRITICAL

        # Hash de mot de passe → HIGH (ou CRITICAL si récent)
        if finding.has_password or finding.has_hash:
            base = Severity.HIGH
            return self._escalate_if_recent(base, finding.breach_date)

        # Données PII uniquement → MEDIUM
        pii_classes = {
            "email addresses",
            "passwords",
            "usernames",
            "phone numbers",
            "physical addresses",
            "dates of birth",
            "social security numbers",
        }
        data_lower = {d.lower() for d in finding.data_classes}
        if data_lower & pii_classes:
            base = Severity.MEDIUM
            return self._escalate_if_recent(base, finding.breach_date)

        # Données non-sensibles ou breach ancienne → LOW
        return Severity.LOW

    @staticmethod
    def _escalate_if_recent(severity: Severity, breach_date: date | None) -> Severity:
        """
        Escalade la sévérité d'un niveau si la breach date de moins de 6 mois.
        Ne peut pas dépasser CRITICAL.
        """
        if not breach_date:
            return severity

        days_old = (date.today() - breach_date).days
        if days_old < 180:  # < 6 mois
            escalation = {
                Severity.LOW: Severity.MEDIUM,
                Severity.MEDIUM: Severity.HIGH,
                Severity.HIGH: Severity.CRITICAL,
                Severity.CRITICAL: Severity.CRITICAL,
            }
            return escalation.get(severity, severity)

        return severity

    def _calculate_global_severity(
        self,
        email_results: list[EmailFindingResult],
        ransom_findings: list[RansomFinding],
    ) -> Severity | None:
        """
        Calcule la sévérité globale du rapport.

        ⚠️  RÈGLE CRITIQUE : La présence d'un seul RansomFinding force CRITICAL.
        """
        if ransom_findings:
            logger.warning(
                f"🚨 Sévérité globale forcée à CRITICAL — {len(ransom_findings)} alerte(s) ransomware détectée(s)"
            )
            return Severity.CRITICAL

        if not email_results:
            return None

        compromised = [r for r in email_results if r.severity is not None]
        if not compromised:
            return None

        return max(r.severity for r in compromised if r.severity)

    def _build_summary(
        self,
        email_results: list[EmailFindingResult],
        ransom_findings: list[RansomFinding],
    ) -> ReportSummary:
        """Construit le bloc de résumé du rapport."""
        compromised = [r for r in email_results if r.is_compromised]
        clean = [r for r in email_results if not r.is_compromised]

        # Répartition par sévérité
        breakdown = SeverityBreakdown()
        for result in compromised:
            if result.severity == Severity.CRITICAL:
                breakdown.CRITICAL += 1
            elif result.severity == Severity.HIGH:
                breakdown.HIGH += 1
            elif result.severity == Severity.MEDIUM:
                breakdown.MEDIUM += 1
            elif result.severity == Severity.LOW:
                breakdown.LOW += 1

        # Breaches les plus fréquentes
        breach_counts: dict[str, int] = defaultdict(int)
        all_dates: list[date] = []

        for result in compromised:
            for finding in result.findings:
                breach_counts[finding.breach_name] += 1
                if finding.breach_date:
                    all_dates.append(finding.breach_date)

        most_common = sorted(
            breach_counts.keys(),
            key=lambda b: breach_counts[b],
            reverse=True,
        )[:5]

        return ReportSummary(
            emails_compromised=len(compromised),
            emails_clean=len(clean),
            severity_breakdown=breakdown,
            most_common_breaches=most_common,
            oldest_breach=str(min(all_dates)) if all_dates else None,
            newest_breach=str(max(all_dates)) if all_dates else None,
        )
