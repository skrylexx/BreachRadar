# How to Add a New OSINT Connector

BreachRadar is designed to be easily extensible. This guide explains how to add a new leak source (OSINT connector) to the backend engine.

---

## 1. Create the Client Class

All connectors must live in `backend/app/clients/` and inherit from `BaseLeakClient`.

### Step 1: Create a new file
Create `backend/app/clients/mysource.py`.

### Step 2: Implement the logic
```python
from app.clients.base import BaseLeakClient
from app.models.finding import LeakFinding, Severity
from app.engine.sanitizer import DataSanitizer

class MySourceClient(BaseLeakClient):
    name = "mysource"  # Unique technical identifier

    def __init__(self, api_key: str, rate_limit_delay: float = 1.0):
        super().__init__()
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.base_url = "https://api.mysource.com/v1"

    async def check_email(self, email: str) -> list[LeakFinding]:
        # 1. Apply rate limit
        await self._apply_rate_limit()

        # 2. Build HTTP client
        headers = {"X-API-Key": self.api_key}
        async with self._build_http_client(headers=headers) as client:
            # 3. Perform request securely
            response = await self._safe_get(client, f"{self.base_url}/search", params={"q": email})
            
            if not response:
                return []

            data = response.json()
            findings = []

            # 4. Parse results into LeakFinding objects
            for item in data.get("results", []):
                findings.append(LeakFinding(
                    source=self.name,
                    email=email,
                    breach_name=item.get("leak_name"),
                    # ... other fields
                    severity=Severity.HIGH
                ))
            
            return findings

    async def check_domain(self, domain: str) -> list[LeakFinding]:
        # Implement domain-wide search if supported by the API
        return []
```

---

## 2. Security Rules (Mandatory)

When implementing a new connector, you **MUST** follow these rules:

1.  **Zero Sensitive Logs**: Never log passwords, hashes, or API keys. Use `self._log_sensitive_data_detected()` if needed.
2.  **Sanitization**: Ensure that data coming from the API is sanitized before being returned.
3.  **Honest User-Agent**: Use the default User-Agent provided by `_build_http_client()`.
4.  **No `verify=False`**: Always verify SSL certificates.

---

## 3. Register the Source

To make your source available in the engine, you need to register it.

### 1. Update `backend/app/core/sources.yaml`
Add your new source to the configuration file so it can be enabled/disabled.

```yaml
sources:
  - name: mysource
    enabled: true
    requires_key: true
    priority: 10
```

### 2. Update `backend/app/engine/source_registry.py`
Instantiate your client in the registry.

```python
from app.clients.mysource import MySourceClient

# Inside the source loading logic:
if source_name == "mysource":
    client = MySourceClient(api_key=config.MYSORCE_API_KEY)
```

---

## 4. Testing Your Connector

Create a test file in `backend/tests/test_clients/test_mysource.py`.

```python
import pytest
from app.clients.mysource import MySourceClient

@pytest.mark.asyncio
async def test_mysource_check_email(htpx_mock):
    # Mock the API response
    htpx_mock.add_response(json={"results": [{"leak_name": "Test Breach"}]})
    
    client = MySourceClient(api_key="fake_key")
    findings = await client.check_email("test@example.com")
    
    assert len(findings) == 1
    assert findings[0].breach_name == "Test Breach"
```

---

## 5. Submit Your PR

1.  Ensure your code is linted: `uv run ruff check .`
2.  Ensure tests pass: `uv run pytest backend/tests/test_clients/test_mysource.py`
3.  Open a PR with the title `feat(backend): add mysource connector`.

Thank you for contributing to BreachRadar! 🛡️
