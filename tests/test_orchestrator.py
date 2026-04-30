"""
Tests unitaires pour l'Orchestrateur (ScanOrchestrator).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from leakmonitor.core.orchestrator import ScanOrchestrator
from leakmonitor.models.finding import LeakFinding, Severity
from leakmonitor.config.settings import Settings
from leakmonitor.config.source_registry import SourceRegistry

@pytest.fixture
def mock_settings():
    settings = Settings(target_domain="example.com", hibp_api_key="dummy_key")
    return settings

@pytest.fixture
def mock_registry():
    registry = SourceRegistry()
    registry.sources["hibp"].is_active = True
    return registry

@pytest.mark.asyncio
async def test_scan_emails(mock_settings, mock_registry):
    orchestrator = ScanOrchestrator(settings=mock_settings, registry=mock_registry)
    
    # Remplacer le client par un mock
    mock_client = AsyncMock()
    mock_client.name = "mock_client"
    mock_client.check_email.return_value = [
        LeakFinding(
            source="mock_client", email="test@example.com", breach_name="Breach1",
            breach_date=None, data_classes=[], has_password=False,
            has_hash=False, has_api_key=False, severity=Severity.LOW, verified=True, is_sensitive=False
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
    
    # L'erreur doit être attrapée et ne pas faire crasher l'orchestrateur
    findings = await orchestrator.scan_emails(["test@example.com"])
    
    assert len(findings) == 0
