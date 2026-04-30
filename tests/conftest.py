"""
tests/conftest.py

Fixtures pytest partagées pour tous les tests BreachRadar.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import respx

from breachradar.models.finding import LeakFinding, Severity
from breachradar.models.ransom import RansomFinding, RansomStats, RansomStatus

# Répertoire des fixtures JSON
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ─── Fixtures RansomLook ──────────────────────────────────────────────────────

@pytest.fixture
def ransom_victim_found_json() -> list[dict]:
    """Réponse API RansomLook simulée — domaine trouvé."""
    with (FIXTURES_DIR / "ransomlook" / "victim_found.json").open() as f:
        return json.load(f)


@pytest.fixture
def ransom_victim_not_found_json() -> list[dict]:
    """Réponse API RansomLook simulée — domaine non trouvé."""
    with (FIXTURES_DIR / "ransomlook" / "victim_not_found.json").open() as f:
        return json.load(f)


@pytest.fixture
def mock_ransom_finding() -> RansomFinding:
    """RansomFinding de test complet."""
    return RansomFinding(
        group_name="lockbit3",
        group_display_name="LockBit 3.0",
        victim_name="MonDomaine SA",
        victim_website="mondomaine.fr",
        discovered_at=datetime(2025, 1, 14, 14, 32, 0),
        published_at=datetime(2025, 1, 14, 14, 32, 0),
        description="500GB of internal data.",
        country="France",
        activity="Technology",
        claim_size="500GB",
        status=RansomStatus.PUBLISHED,
        portal_url="http://lockbit3abc.onion/post/abc123",
        search_term_matched="mondomaine.fr",
    )


@pytest.fixture
def mock_ransom_stats_healthy() -> RansomStats:
    """Statistiques RansomLook — instance saine."""
    return RansomStats(
        groups_tracked=124,
        total_posts=16340,
        last_update=datetime(2025, 1, 15, 7, 45, 0),
        instance_url="http://localhost:8888",
        is_healthy=True,
    )


@pytest.fixture
def mock_ransom_stats_unhealthy() -> RansomStats:
    """Statistiques RansomLook — instance inaccessible."""
    return RansomStats(
        groups_tracked=0,
        total_posts=0,
        last_update=None,
        instance_url="http://localhost:8888",
        is_healthy=False,
    )


# ─── Fixtures LeakFinding ─────────────────────────────────────────────────────

@pytest.fixture
def mock_finding_critical() -> LeakFinding:
    """LeakFinding de sévérité CRITICAL (credential en clair)."""
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


@pytest.fixture
def mock_finding_high() -> LeakFinding:
    """LeakFinding de sévérité HIGH (hash de mot de passe)."""
    return LeakFinding(
        source="hibp",
        email="bob@mondomaine.fr",
        breach_name="Adobe",
        breach_date=date(2013, 10, 4),
        data_classes=["Email addresses", "Password hints"],
        has_password=False,
        has_hash=True,
        has_api_key=False,
        has_plaintext_credential=False,
        severity=Severity.HIGH,
        verified=True,
    )


@pytest.fixture
def mock_finding_low() -> LeakFinding:
    """LeakFinding de sévérité LOW (données non-sensibles)."""
    return LeakFinding(
        source="hibp",
        email="charlie@mondomaine.fr",
        breach_name="OldService",
        breach_date=date(2019, 6, 1),
        data_classes=["Email addresses", "Usernames"],
        has_password=False,
        has_hash=False,
        has_api_key=False,
        has_plaintext_credential=False,
        severity=Severity.LOW,
        verified=True,
    )


# ─── Fixtures Mock Clients ────────────────────────────────────────────────────

@pytest.fixture
def mock_notifier() -> MagicMock:
    """NotificationEngine mocké."""
    notifier = MagicMock()
    notifier.send_ransom_alert = AsyncMock(return_value=None)
    notifier.send_email = AsyncMock(return_value=None)
    notifier.send_webhook = AsyncMock(return_value=None)
    return notifier


@pytest.fixture
def test_domain() -> str:
    """Domaine de test standard."""
    return "mondomaine.fr"
