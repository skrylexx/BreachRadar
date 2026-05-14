import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class FindingRead(BaseModel):
    id: str
    severity: str
    source: str
    domain: str
    type: str
    count: Optional[int] = None
    discovered_at: datetime
    metadata: Optional[Dict[str, Any]] = None
