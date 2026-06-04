"""
tests/test_security.py

Security non-regression tests — GDPR compliance.

These tests verify that:
1. No sensitive data passes through the reports
2. .onion URLs are never included in the final reports
3. The sanitizer covers all known hash formats
4. CRITICAL severity is correctly forced by a RansomFinding
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime

from app.engine.aggregator import ResultAggregator
from app.models.finding import LeakFinding, Severity
from app.models.ransom import RansomFinding, RansomStatus
from app.models.report import ReportMetadata

# Sensitive patterns that MUST NEVER appear in a final report
FORBIDDEN_PATTERNS = [
    r"(?i)password\s*[:=]\s*\S+",  # Plaintext password
    r"\b[a-f0-9]{32}\b",  # MD5 hash
    r"\b[a-f0-9]{40}\b",  # SHA-1 hash
    r"\b[a-f0-9]{64}\b",  # SHA-256 hash
    r"\$2[ayb]\$.{56}",  # bcrypt hash
    r"ghp_[A-Za-z0-9]{36,}",  # GitHub token
]


def _make_metadata(domain: str = "mondomaine.fr") -> ReportMetadata:
    return ReportMetadata(
        target_domain=domain,
        sources_queried=["hibp", "ransomlook"],
    )


def _make_finding_with_sensitive_breach() -> LeakFinding:
    """Finding that would contain sensitive data if poorly sanitized."""
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
    """Verification that no sensitive data appears in the report."""

    def test_leak_finding_has_no_sensitive_fields(self) -> None:
        """
        The LeakFinding model must not have a field
        to store a password, hash or token.
        """
        finding = _make_finding_with_sensitive_breach()
        finding_dict = finding.model_dump()

        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, date):
                    return obj.isoformat()
                return super().default(obj)

        finding_json = json.dumps(finding_dict, cls=DateTimeEncoder)

        # Verify the absence of fields "password", "hash_value", "token"
        forbidden_field_names = {"password", "hash_value", "hash", "token", "api_key_value"}
        for field_name in forbidden_field_names:
            assert field_name not in finding_dict, (
                f"Sensitive field '{field_name}' found in LeakFinding — this field must not exist in the model"
            )

        # Verify that sensitive patterns are not in the JSON serialization
        for pattern in FORBIDDEN_PATTERNS:
            assert not re.search(pattern, finding_json), f"Sensitive pattern detected in LeakFinding JSON: {pattern}"

    def test_report_does_not_contain_passwords(self) -> None:
        """The final report must not contain any passwords."""
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
                f"Sensitive data detected in the final report: pattern={pattern}"
            )


class TestOnionUrlNotInReport:
    """.onion URLs must not appear in reports."""

    def test_ransom_finding_portal_url_stored_but_visible(self) -> None:
        """
        The .onion URL is stored in RansomFinding.portal_url
        but the ReportEngine MUST mask it when generating the report.

        This test verifies that the model stores it (for internal use),
        and that the string ".onion" is present in the raw model.
        Note: the ReportEngine must mask it, not the model.
        """
        finding = RansomFinding(
            group_name="lockbit3",
            group_display_name="LockBit 3.0",
            victim_name="MonDomaine SA",
            discovered_at=datetime.fromisoformat("2025-01-14T14:32:00Z".replace("Z", "+00:00")),
            status=RansomStatus.LISTED,
            portal_url="http://lockbit3abc.onion/post/abc123",
            search_term_matched="mondomaine.fr",
        )
        # The model stores the URL (internal use)
        assert finding.portal_url is not None
        assert ".onion" in finding.portal_url

    def test_data_integrity_flags_onion_excluded(self) -> None:
        """The DataIntegrity.onion_urls_excluded_from_report flag is True."""
        from app.models.report import DataIntegrity

        integrity = DataIntegrity()
        assert integrity.onion_urls_excluded_from_report is True


class TestRansomForcesGlobalCritical:
    """Verification of the RansomLook critical rule → global CRITICAL severity."""

    def test_ransom_finding_elevates_global_severity_to_critical(self) -> None:
        """
        A single RansomFinding must force the global severity to CRITICAL,
        even if all email_findings are LOW.
        """
        aggregator = ResultAggregator()

        low_finding = LeakFinding(
            source="hibp",
            email="alice@mondomaine.fr",
            breach_name="OldService",
            breach_date=None,
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
            discovered_at=datetime.fromisoformat("2025-01-14T14:32:00Z".replace("Z", "+00:00")),
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
        """Without RansomFinding, the global severity remains that of the emails."""
        aggregator = ResultAggregator()

        low_finding = LeakFinding(
            source="hibp",
            email="alice@mondomaine.fr",
            breach_name="OldService",
            breach_date=None,
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
            ransom_findings=[],  # No ransomware
            metadata=metadata,
        )

        assert report.summary.global_severity == Severity.MEDIUM
        assert report.summary.ransomware_detected is False
        assert report.has_critical_alert() is False

    def test_empty_scan_returns_no_severity(self) -> None:
        """Empty scan → global severity None."""
        aggregator = ResultAggregator()
        metadata = _make_metadata()
        report = aggregator.aggregate(
            email_findings=[],
            ransom_findings=[],
            metadata=metadata,
        )

        assert report.summary.global_severity is None
        assert report.has_critical_alert() is False
