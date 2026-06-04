"""
backend/tests/test_cve_monitor.py

Unit tests for the CVE watch engine (CVEMonitor).
Uses respx to mock external API calls.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import respx
from httpx import Response

from app.engine.cve_monitor import CVEMonitor
from app.models.cve import CVEAlert, CVESeverity, CVESourceType


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()

    # Mock the select result for the upsert (None by default = new CVE)
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    return db


@pytest.mark.asyncio
async def test_poll_nvd_success(mock_db):
    monitor = CVEMonitor(mock_db)

    nvd_response = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2024-1234",
                    "descriptions": [{"lang": "en", "value": "Test NVD vulnerability"}],
                    "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}]},
                    "published": "2024-05-17T10:00:00.000Z",
                }
            }
        ]
    }

    with respx.mock:
        respx.get("https://services.nvd.nist.gov/rest/json/cves/2.0").mock(
            return_value=Response(200, json=nvd_response)
        )

        await monitor._poll_nvd(["nvd_windows"])

    assert mock_db.add.called
    alert = mock_db.add.call_args[0][0]
    assert alert.cve_id == "CVE-2024-1234"
    assert alert.severity == CVESeverity.CRITICAL
    assert alert.cvss_score == 9.8
    assert alert.source_type == CVESourceType.NVD


@pytest.mark.asyncio
async def test_poll_github_advisories_success(mock_db):
    monitor = CVEMonitor(mock_db)

    # Mock Atom feed
    atom_content = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>GHSA-1234-5678</id>
        <title>CVE-2024-5678: GitHub Advisory Title</title>
        <link href="https://github.com/advisories/GHSA-1234-5678" />
        <summary>Vulnerability description from GitHub</summary>
        <updated>2024-05-17T12:00:00Z</updated>
      </entry>
    </feed>
    """

    with respx.mock:
        respx.get("https://github.com/advisories.atom?query=type%3Areviewed").mock(
            return_value=Response(200, text=atom_content)
        )

        await monitor._poll_github_advisories()

    assert mock_db.add.called
    alert = mock_db.add.call_args[0][0]
    assert alert.cve_id == "CVE-2024-5678"
    assert "GitHub Advisory Title" in alert.title
    assert alert.source_type == CVESourceType.GITHUB


@pytest.mark.asyncio
async def test_poll_osv_success(mock_db):
    monitor = CVEMonitor(mock_db)

    # OSV flow: 1. Fetch CSV with IDs, 2. Fetch detail for each ID
    csv_content = "2024-05-17T10:00:00Z,OSV-2024-9999\n"
    osv_detail = {
        "id": "OSV-2024-9999",
        "summary": "OSV Summary",
        "details": "OSV Full Details",
        "published": "2024-05-17T10:00:00Z",
        "database_specific": {"severity": "HIGH"},
    }

    with respx.mock:
        respx.get("https://storage.googleapis.com/osv-vulnerabilities/PyPI/modified_id.csv").mock(
            return_value=Response(200, text=csv_content)
        )
        respx.get("https://api.osv.dev/v1/vulns/OSV-2024-9999").mock(return_value=Response(200, json=osv_detail))

        await monitor._poll_osv(["osv_pypi"])

    assert mock_db.add.called
    alert = mock_db.add.call_args[0][0]
    assert alert.cve_id == "OSV-2024-9999"
    assert alert.severity == CVESeverity.HIGH
    assert alert.source_type == CVESourceType.OSV


@pytest.mark.asyncio
async def test_poll_cvefeed_success(mock_db):
    monitor = CVEMonitor(mock_db)

    # CVEFeed RSS
    rss_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>CVE-2024-9876: Critical bug</title>
          <link>https://cvefeed.io/vuln/CVE-2024-9876</link>
          <description>Critical vulnerability from CVEFeed</description>
          <pubDate>Fri, 17 May 2024 14:00:00 +0000</pubDate>
        </item>
      </channel>
    </rss>
    """

    with respx.mock:
        respx.get("https://cvefeed.io/rssfeed/severity/critical.xml").mock(return_value=Response(200, text=rss_content))
        respx.get("https://cvefeed.io/rssfeed/severity/high.xml").mock(return_value=Response(200, text=""))

        await monitor._poll_cvefeed()

    assert mock_db.add.called
    alert = mock_db.add.call_args[0][0]
    assert alert.cve_id == "CVE-2024-9876"
    assert alert.severity == CVESeverity.CRITICAL
    assert alert.source_type == CVESourceType.CVEFEED


@pytest.mark.asyncio
async def test_upsert_existing_cve(mock_db):
    # Mock existing CVE in DB
    existing_alert = CVEAlert(
        cve_id="CVE-2024-0000",
        title="Old Title",
        description="Old Description",
        severity=CVESeverity.LOW,
        published_at=datetime.now(UTC),
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_alert
    mock_db.execute.return_value = mock_result

    monitor = CVEMonitor(mock_db)
    new_alert = CVEAlert(
        cve_id="CVE-2024-0000",
        title="New Title",
        description="New Description",
        severity=CVESeverity.HIGH,
        published_at=datetime.now(UTC),
    )

    await monitor._upsert_cve(new_alert)

    # add should NOT be called
    assert not mock_db.add.called
    # existing_alert should be updated
    assert existing_alert.title == "New Title"
    assert existing_alert.severity == CVESeverity.HIGH
