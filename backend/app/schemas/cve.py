from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

class CVESeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

class CVESource(str, Enum):
    NVD = "NVD"
    OSV = "OSV"
    GITHUB = "GitHub"
    CVEFEED = "CVEFeed"
    CUSTOM = "Custom"

class CVEAlert(BaseModel):
    id: str
    cve_id: str
    title: str
    description: str
    severity: CVESeverity
    cvss_score: Optional[float] = None
    category: str
    source: CVESource
    url: str
    published_at: datetime

class CVESettings(BaseModel):
    active_categories: List[str]
    nvd_api_key: Optional[str] = None
    polling_interval_minutes: int = 60
    include_no_cvss: bool = False

class CVESourceStatus(BaseModel):
    source: CVESource
    status: str  # "ok", "error", "degraded"
    last_sync_at: Optional[datetime] = None
    count: int = 0
    message: Optional[str] = None
