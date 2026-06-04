"""
breachradar/core/aggregator.py

Deduplication and aggregation of findings.

Responsibilities:
1. Deduplicate identical findings from multiple sources
2. Calculate severity per email (based on types of data exposed)
3. Calculate the overall severity of the report
4. Integrate RansomFindings as a global maximum severity signal

CRITICAL RULE RansomLook:
If a RansomFinding is present, the OVERALL severity is ALWAYS CRITICAL.
This rule is non-negotiable — a ransomware compromise in progress
is the most serious scenario possible.
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

# Generic recommendations by severity level
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
    Aggregates, deduplicates and calculates the severities of findings.

    Usage:
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
        Primary entry point — produces the full FinalReport.

        ⚠️ CRITICAL RULE: If ransom_findings is non-empty, the severity
        global is CRITICAL regardless of the severity of email_findings.

        Args:
            email_findings: All email findings (all sources)
            ransom_findings: Findings RansomLook (may be empty)
            metadata: Scan metadata

        Returns:
            FinalReport complete and ready to be rendered
        """
        # 1. Deduplicate and consolidate findings by email
        email_results = self._deduplicate_and_group(email_findings)

        # 2. Calculate the severity of each email
        for result in email_results.values():
            result.severity = self._calculate_email_severity(result.findings)
            result.recommendations = SEVERITY_RECOMMENDATIONS.get(result.severity, [])

        # 3. Build the ransomware alert block
        ransomware_alerts = RansomwareAlerts(
            domain_listed=len(ransom_findings) > 0,
            alert_count=len(ransom_findings),
            alerts=ransom_findings,
        )

        # 4. Calculate overall severity
        global_severity = self._calculate_global_severity(list(email_results.values()), ransom_findings)

        # 5. Build the summary
        summary = self._build_summary(list(email_results.values()), ransom_findings)
        summary.global_severity = global_severity
        summary.ransomware_detected = len(ransom_findings) > 0

        # 6. Sort findings by severity (CRITICAL first)
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
        Group findings by email and deduplicate identical breaches.
        A breach is a duplicate if (email, breach_name, source) is the same.

        Returns:
            Email Dictionary → Deduplicated EmailFindingResult
        """
        grouped: dict[str, list[LeakFinding]] = defaultdict(list)
        seen_breaches: dict[str, set[tuple[str, str]]] = defaultdict(set)

        for finding in findings:
            # Deduplication key: (breach_name, source)
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
        Calculates the maximum severity for a given email.

        Rules (in descending order of priority):
        - Clear credential or API key → CRITICAL
        - Password hash → HIGH (+ escalation if recent)
        - PII data only → MEDIUM
        - Non-sensitive data, old breach → LOW

        The severity is increased by one level if the breach is recent (<6 months).
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
        """Calculates the severity of an individual LeakFinding."""
        # Clear credential or API key → immediate CRITICAL
        if finding.has_plaintext_credential or finding.has_api_key:
            return Severity.CRITICAL

        # Password hash → HIGH (or CRITICAL if recent)
        if finding.has_password or finding.has_hash:
            base = Severity.HIGH
            return self._escalate_if_recent(base, finding.breach_date)

        # PII data only → MEDIUM
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

        # Non-sensitive data or old breach → LOW
        return Severity.LOW

    @staticmethod
    def _escalate_if_recent(severity: Severity, breach_date: date | None) -> Severity:
        """
        Escalate the severity by one level if the breach is less than 6 months old.
        Cannot exceed CRITICAL.
        """
        if not breach_date:
            return severity

        days_old = (date.today() - breach_date).days
        if days_old < 180:  # < 6 months
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
        Calculates the overall severity of the report.

        ⚠️ CRITICAL RULE: The presence of a single RansomFinding forces CRITICAL.
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
        """Constructs the report summary block."""
        compromised = [r for r in email_results if r.is_compromised]
        clean = [r for r in email_results if not r.is_compromised]

        # Distribution by severity
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

        # Most common breaches
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
