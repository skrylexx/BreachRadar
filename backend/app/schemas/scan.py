"""
BreachRadar WebUI — Scan Schemas (Pydantic)
==========================================
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.models.scan import ScanSeverity, ScanStatus


class ScanResultRead(BaseModel):
    """Scan result exposed via the API."""

    id: uuid.UUID
    target_domain: str
    status: ScanStatus
    severity: ScanSeverity | None
    total_findings: int
    ransomware_findings: int
    breach_findings: int
    findings_by_source: dict[str, int] | None
    triggered_by: str
    started_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ScanStats(BaseModel):
    """Aggregated statistics for dashboard charts."""

    # Data for the bar chart (7d, 1 month, 6 months, 12 months)
    period: str  # "7d" | "1m" | "6m" | "12m"
    data_points: list[dict]  # [{"date": "2026-01-15", "total": 12, "critical": 2, ...}]
    summary: dict  # Totals over the period

    model_config = {"from_attributes": True}


class ScanTriggerRequest(BaseModel):
    """Manual trigger of a scan (admin only)."""

    target_domain: str | None = None  # If None, uses the configured domain

    @field_validator("target_domain")
    @classmethod
    def validate_domain(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Simple domain validation to prevent SSRF and injections
        # Must contain at least one dot, no spaces, no suspicious special characters
        if not re.match(r"^[a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid target domain format")
        if v:
            # Forbid localhost and local IPs to prevent SSRF
            blacklist = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]  # nosec B104
            if v.lower() in blacklist:
                raise ValueError("Target domain cannot be a local address")
        return v


class ScanTriggerResponse(BaseModel):
    """Response to triggering a scan."""

    scan_id: uuid.UUID
    message: str = "Scan triggered successfully"
    started_at: datetime
