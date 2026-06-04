"""
Unit tests for the Orchestrator (ScanOrchestrator).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Settings
from app.core.source_registry import SourceRegistry
from app.engine.orchestrator import ScanOrchestrator
from app.models.finding import LeakFinding, Severity


@pytest.fixture
def mock_settings():
    return Settings(target_domain="example.com", hibp_api_key="dummy_key")


@pytest.fixture
def mock_registry():
    registry = MagicMock(spec=SourceRegistry)
    # We simulate a dictionary of sources
    registry.sources = {}
    return registry


@pytest.mark.asyncio
async def test_scan_emails(mock_settings, mock_registry):
    orchestrator = ScanOrchestrator(settings=mock_settings, registry=mock_registry)

    # Replace the client with a mock
    mock_client = AsyncMock()
    mock_client.name = "mock_client"
    mock_client.check_email.return_value = [
        LeakFinding(
            source="mock_client",
            email="test@example.com",
            breach_name="Breach1",
            breach_date=None,
            data_classes=[],
            has_password=False,
            has_hash=False,
            has_api_key=False,
            severity=Severity.LOW,
            verified=True,
            is_sensitive=False,
        )
    ]

    orchestrator.clients = [mock_client]

    findings = await orchestrator.scan_emails(["test@example.com"])

    assert len(findings) == 1
    assert findings[0].email == "test@example.com"
    mock_client.check_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_scan_domain(mock_settings, mock_registry):
    orchestrator = ScanOrchestrator(settings=mock_settings, registry=mock_registry)

    mock_client = AsyncMock()
    mock_client.name = "mock_client"
    mock_client.check_domain.return_value = []

    orchestrator.clients = [mock_client]

    findings = await orchestrator.scan_domain("example.com")

    assert len(findings) == 0
    mock_client.check_domain.assert_called_once_with("example.com")


@pytest.mark.asyncio
async def test_scan_client_error_handling(mock_settings, mock_registry):
    orchestrator = ScanOrchestrator(settings=mock_settings, registry=mock_registry)

    mock_client = AsyncMock()
    mock_client.name = "mock_client"
    mock_client.check_email.side_effect = Exception("Simulated error")

    orchestrator.clients = [mock_client]

    # The error must be caught and not crash the orchestrator
    findings = await orchestrator.scan_emails(["test@example.com"])

    assert len(findings) == 0
