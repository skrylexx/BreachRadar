"""
Unit tests for the aggregator (ResultAggregator).
"""

from datetime import UTC, date, datetime

import pytest

from app.engine.aggregator import ResultAggregator
from app.models.finding import LeakFinding, Severity
from app.models.ransom import RansomFinding, RansomStatus
from app.models.report import ReportMetadata


@pytest.fixture
def aggregator():
    return ResultAggregator()


@pytest.fixture
def dummy_metadata():
    return ReportMetadata(
        target_domain="example.com",
        sources_queried=["test"],
        scan_duration_seconds=1.0,
        total_emails_checked=1,
        total_findings=0,
    )


def test_deduplication(aggregator, dummy_metadata):
    """Verifies that identical findings (same email, same breach, same source) are deduplicated."""
    findings = [
        LeakFinding(
            source="test",
            email="admin@example.com",
            breach_name="Breach1",
            breach_date=None,
            data_classes=["Emails"],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            severity=Severity.LOW,
            verified=True,
            is_sensitive=False,
        ),
        LeakFinding(
            source="test",
            email="admin@example.com",
            breach_name="Breach1",
            breach_date=None,
            data_classes=["Emails"],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            severity=Severity.LOW,
            verified=True,
            is_sensitive=False,
        ),
    ]
    report = aggregator.aggregate(email_findings=findings, ransom_findings=[], metadata=dummy_metadata)

    assert len(report.findings) == 1
    assert report.findings[0].breach_count == 1
    assert len(report.findings[0].findings) == 1


def test_severity_calculation(aggregator, dummy_metadata):
    """Verifies the calculation of severity per email and globally."""
    findings = [
        LeakFinding(
            source="test",
            email="user@example.com",
            breach_name="Breach_Low",
            breach_date=date(2020, 1, 1),
            data_classes=["Emails"],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            severity=Severity.LOW,
            verified=True,
            is_sensitive=False,
        ),
        LeakFinding(
            source="test",
            email="admin@example.com",
            breach_name="Breach_High",
            breach_date=date(2020, 1, 1),
            data_classes=["Emails", "Passwords"],
            has_password=True,
            has_hash=False,
            has_api_key=False,
            severity=Severity.HIGH,
            verified=True,
            is_sensitive=True,
        ),
    ]
    report = aggregator.aggregate(email_findings=findings, ransom_findings=[], metadata=dummy_metadata)

    assert len(report.findings) == 2
    # One has LOW, the other has HIGH (potentially CRITICAL if recent, but here 2020 so HIGH)
    severities = {f.email: f.severity for f in report.findings}
    assert severities["user@example.com"] == Severity.LOW
    assert severities["admin@example.com"] == Severity.HIGH
    assert report.summary.global_severity == Severity.HIGH


def test_ransomware_overrides_severity(aggregator, dummy_metadata):
    """Verifies that a RansomFinding forces the global severity to CRITICAL."""
    ransom_findings = [
        RansomFinding(
            source="ransomlook",
            group_name="lockbit3",
            group_display_name="LockBit 3.0",
            victim_name="Example",
            victim_website="example.com",
            discovered_at=datetime.now(UTC),
            published_at=None,
            description=None,
            country=None,
            activity=None,
            claim_size=None,
            status=RansomStatus.LISTED,
            portal_url=None,
            search_term_matched="example.com",
            severity="CRITICAL",
        )
    ]
    # Even without email findings
    report = aggregator.aggregate(email_findings=[], ransom_findings=ransom_findings, metadata=dummy_metadata)

    assert report.summary.global_severity == Severity.CRITICAL
    assert report.summary.ransomware_detected is True
    assert len(report.ransomware_alerts.alerts) == 1


def test_escalate_recent_breach(aggregator, dummy_metadata):
    """Verifies severity escalation for a recent leak (< 6 months)."""
    findings = [
        LeakFinding(
            source="test",
            email="admin@example.com",
            breach_name="Recent_Breach",
            breach_date=date.today(),
            data_classes=["Emails", "Passwords"],
            has_password=True,
            has_hash=False,
            has_api_key=False,
            severity=Severity.HIGH,
            verified=True,
            is_sensitive=True,
        )
    ]
    report = aggregator.aggregate(email_findings=findings, ransom_findings=[], metadata=dummy_metadata)

    assert report.findings[0].severity == Severity.CRITICAL
    assert report.summary.global_severity == Severity.CRITICAL
