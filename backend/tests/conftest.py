"""
tests/conftest.py

Shared pytest fixtures for all BreachRadar tests.
"""

from __future__ import annotations

import json

# ─── Global Environment Setup ────────────────────────────────────────────────
import os
from datetime import date, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/breachradar"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "dev_secret_key_at_least_32_characters_long"
os.environ["ENCRYPTION_KEY"] = "knkoNM10_D0QLRM8PHihA23w0k50EQnUGwtmqRmbLyY="
os.environ["INITIAL_ADMIN_EMAIL"] = "admin@example.com"
os.environ["INITIAL_ADMIN_PASSWORD"] = "InitialAdminPassword123!"
os.environ["TELEGRAM_API_ID"] = "0"

# ─── Mock Global System ──────────────────────────────────────────────────────
from unittest.mock import patch

from app.models.finding import LeakFinding, Severity
from app.models.ransom import RansomFinding, RansomStats, RansomStatus

# Mock engine and initialize_database globally before any app import
patch("app.core.database.engine").start()
patch("app.core.init_db.initialize_database", new_callable=AsyncMock).start()

# JSON fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ─── RansomLook Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def ransom_victim_found_json() -> list[dict]:
    """Simulated RansomLook API response — domain found."""
    with (FIXTURES_DIR / "ransomlook" / "victim_found.json").open() as f:
        return json.load(f)


@pytest.fixture
def ransom_victim_not_found_json() -> list[dict]:
    """Simulated RansomLook API response — domain not found."""
    with (FIXTURES_DIR / "ransomlook" / "victim_not_found.json").open() as f:
        return json.load(f)


@pytest.fixture
def mock_ransom_finding() -> RansomFinding:
    """Complete test RansomFinding."""
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
    """RansomLook statistics — healthy instance."""
    return RansomStats(
        groups_tracked=124,
        total_posts=16340,
        last_update=datetime(2025, 1, 15, 7, 45, 0),
        instance_url="http://localhost:8888",
        is_healthy=True,
    )


@pytest.fixture
def mock_ransom_stats_unhealthy() -> RansomStats:
    """RansomLook statistics — inaccessible instance."""
    return RansomStats(
        groups_tracked=0,
        total_posts=0,
        last_update=None,
        instance_url="http://localhost:8888",
        is_healthy=False,
    )


# ─── LeakFinding Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def mock_finding_critical() -> LeakFinding:
    """LeakFinding of CRITICAL severity (plaintext credential)."""
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
    """LeakFinding of HIGH severity (password hash)."""
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
    """LeakFinding of LOW severity (non-sensitive data)."""
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


# ─── Mock Clients Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def mock_notifier() -> MagicMock:
    """Mocked NotificationEngine."""
    notifier = MagicMock()
    notifier.send_ransom_alert = AsyncMock(return_value=None)
    notifier.send_email = AsyncMock(return_value=None)
    notifier.send_webhook = AsyncMock(return_value=None)
    return notifier


from app.main import app


@pytest.fixture(autouse=True)
def manage_overrides():
    """Manages the cleanup of overrides between tests."""
    yield
    app.dependency_overrides.clear()
