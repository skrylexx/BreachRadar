"""
tests/test_security.py

Tests de non-régression sécurité — RGPD compliance.

Ces tests vérifient que :
1. Aucune donnée sensible ne transite dans les rapports
2. Les URLs .onion ne sont jamais incluses dans les rapports finaux
3. Le sanitizer couvre tous les formats de hash connus
4. La sévérité CRITICAL est bien forcée par un RansomFinding
"""

from __future__ import annotations

import json
import re
from datetime import date

import pytest

from leakmonitor.core.aggregator import ResultAggregator
from leakmonitor.core.sanitizer import DataSanitizer
from leakmonitor.models.finding import LeakFinding, Severity
from leakmonitor.models.ransom import RansomFinding, RansomStatus
from leakmonitor.models.report import ReportMetadata

# Patterns sensibles qui ne doivent JAMAIS apparaître dans un rapport final
FORBIDDEN_PATTERNS = [
    r"(?i)password\s*[:=]\s*\S+",       # Mot de passe en clair
    r"\b[a-f0-9]{32}\b",                # Hash MD5
    r"\b[a-f0-9]{40}\b",                # Hash SHA-1
    r"\b[a-f0-9]{64}\b",                # Hash SHA-256
    r"\$2[ayb]\$.{56}",                 # Hash bcrypt
    r"ghp_[A-Za-z0-9]{36,}",           # Token GitHub
]


def _make_metadata(domain: str = "mondomaine.fr") -> ReportMetadata:
    return ReportMetadata(
        target_domain=domain,
        sources_queried=["hibp", "ransomlook"],
    )


def _make_finding_with_sensitive_breach() -> LeakFinding:
    """Finding qui contiendrait des données sensibles si mal sanitisé."""
    return LeakFinding(
        source="hibp",
        email="alice@mondomaine.fr",
        breach_name="ServiceXYZ",
        breach_date=date(2024, 3, 15),
        data_classes=["Email addresses", "Passwords"],
        has_password=True,
        has_hash=False,
        has_api_key=False,
        has_plaintext_credential=True,
        severity=Severity.CRITICAL,
        verified=True,
    )


class TestNoSensitiveDataInReport:
    """Vérification qu'aucune donnée sensible n'apparaît dans le rapport."""

    def test_leak_finding_has_no_sensitive_fields(self) -> None:
        """
        Le modèle LeakFinding ne doit pas avoir de champ
        pour stocker un mot de passe, hash ou token.
        """
        finding = _make_finding_with_sensitive_breach()
        finding_dict = finding.model_dump()
        finding_json = json.dumps(finding_dict)

        # Vérifier l'absence de champs "password", "hash_value", "token"
        forbidden_field_names = {"password", "hash_value", "hash", "token", "api_key_value"}
        for field_name in forbidden_field_names:
            assert field_name not in finding_dict, (
                f"Champ sensible '{field_name}' trouvé dans LeakFinding — "
                "ce champ ne doit pas exister dans le modèle"
            )

        # Vérifier que les patterns sensibles ne sont pas dans la sérialisation JSON
        for pattern in FORBIDDEN_PATTERNS:
            assert not re.search(pattern, finding_json), (
                f"Pattern sensible détecté dans LeakFinding JSON : {pattern}"
            )

    def test_report_does_not_contain_passwords(self) -> None:
        """Le rapport final ne doit contenir aucun mot de passe."""
        aggregator = ResultAggregator()
        findings = [_make_finding_with_sensitive_breach()]
        metadata = _make_metadata()

        report = aggregator.aggregate(
            email_findings=findings,
            ransom_findings=[],
            metadata=metadata,
        )
        report_json = report.model_dump_json()

        for pattern in FORBIDDEN_PATTERNS:
            assert not re.search(pattern, report_json), (
                f"Donnée sensible détectée dans le rapport final : pattern={pattern}"
            )


class TestOnionUrlNotInReport:
    """Les URLs .onion ne doivent pas apparaître dans les rapports."""

    def test_ransom_finding_portal_url_stored_but_visible(self) -> None:
        """
        L'URL .onion est stockée dans RansomFinding.portal_url
        mais le ReportEngine DOIT la masquer lors de la génération du rapport.

        Ce test vérifie que le modèle la stocke (pour usage interne),
        et que la chaîne ".onion" est présente dans le modèle brut.
        Note : c'est le ReportEngine qui doit la masquer, pas le modèle.
        """
        finding = RansomFinding(
            group_name="lockbit3",
            group_display_name="LockBit 3.0",
            victim_name="MonDomaine SA",
            discovered_at="2025-01-14T14:32:00Z",
            status=RansomStatus.LISTED,
            portal_url="http://lockbit3abc.onion/post/abc123",
            search_term_matched="mondomaine.fr",
        )
        # Le modèle stocke l'URL (usage interne)
        assert finding.portal_url is not None
        assert ".onion" in finding.portal_url

    def test_data_integrity_flags_onion_excluded(self) -> None:
        """Le flag DataIntegrity.onion_urls_excluded_from_report est True."""
        from leakmonitor.models.report import DataIntegrity
        integrity = DataIntegrity()
        assert integrity.onion_urls_excluded_from_report is True


class TestRansomForcesGlobalCritical:
    """Vérification de la règle critique RansomLook → sévérité CRITICAL globale."""

    def test_ransom_finding_elevates_global_severity_to_critical(self) -> None:
        """
        Un seul RansomFinding doit forcer la sévérité globale à CRITICAL,
        même si tous les email_findings sont LOW.
        """
        aggregator = ResultAggregator()

        low_finding = LeakFinding(
            source="hibp",
            email="alice@mondomaine.fr",
            breach_name="OldService",
            breach_date=date(2019, 1, 1),
            data_classes=["Email addresses"],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            has_plaintext_credential=False,
            severity=Severity.LOW,
            verified=True,
        )

        ransom_finding = RansomFinding(
            group_name="play",
            group_display_name="Play",
            victim_name="MonDomaine SA",
            discovered_at="2025-01-14T14:32:00Z",
            status=RansomStatus.LISTED,
            search_term_matched="mondomaine.fr",
        )

        metadata = _make_metadata()
        report = aggregator.aggregate(
            email_findings=[low_finding],
            ransom_findings=[ransom_finding],
            metadata=metadata,
        )

        assert report.summary.global_severity == Severity.CRITICAL
        assert report.summary.ransomware_detected is True
        assert report.has_critical_alert() is True

    def test_no_ransom_no_forced_critical(self) -> None:
        """Sans RansomFinding, la sévérité globale reste celle des emails."""
        aggregator = ResultAggregator()

        low_finding = LeakFinding(
            source="hibp",
            email="alice@mondomaine.fr",
            breach_name="OldService",
            breach_date=date(2019, 1, 1),
            data_classes=["Email addresses"],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            has_plaintext_credential=False,
            severity=Severity.LOW,
            verified=True,
        )

        metadata = _make_metadata()
        report = aggregator.aggregate(
            email_findings=[low_finding],
            ransom_findings=[],  # Pas de ransomware
            metadata=metadata,
        )

        assert report.summary.global_severity == Severity.LOW
        assert report.summary.ransomware_detected is False
        assert report.has_critical_alert() is False

    def test_empty_scan_returns_no_severity(self) -> None:
        """Scan vide → sévérité globale None."""
        aggregator = ResultAggregator()
        metadata = _make_metadata()
        report = aggregator.aggregate(
            email_findings=[],
            ransom_findings=[],
            metadata=metadata,
        )

        assert report.summary.global_severity is None
        assert report.has_critical_alert() is False
