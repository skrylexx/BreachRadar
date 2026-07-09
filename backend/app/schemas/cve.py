from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, AliasChoices
import uuid

class CVESeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class CVESource(StrEnum):
    NVD = "NVD"
    OSV = "OSV"
    GITHUB = "GitHub"
    CVEFEED = "CVEFeed"
    CUSTOM = "Custom"


class CVEAlert(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID | str
    cve_id: str
    title: str
    description: str
    severity: CVESeverity
    cvss_score: float | None = None
    category: str
    source: CVESource = Field(validation_alias=AliasChoices("source_type", "source"))
    url: str
    published_at: datetime
    comment: str | None = None


class CVEAlertUpdate(BaseModel):
    comment: str


class CVESettings(BaseModel):
    active_categories: list[str]
    nvd_api_key: str | None = None
    polling_interval_minutes: int = 60
    include_no_cvss: bool = False


class CVESourceStatus(BaseModel):
    source: CVESource
    status: str  # "ok", "error", "degraded"
    last_sync_at: datetime | None = None
    count: int = 0
    message: str | None = None
