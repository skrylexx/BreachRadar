# BreachRadar — Backend API

This directory contains the core of the BreachRadar application: the FastAPI API and the OSINT orchestration engine.

## 🚀 Technologies Used

- **Language**: Python 3.12+
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous)
- **Database**: PostgreSQL with [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Asyncio)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Schemas**: [Pydantic v2](https://docs.pydantic.dev/)
- **Security**: JWT (HS256), BCrypt, MFA TOTP ([PyOTP](https://github.com/pyauth/pyotp))
- **Task Management**: [APScheduler](https://apscheduler.agronholm.net/) for scheduled scans
- **Cache & Rate Limiting**: [Redis](https://redis.io/) with [SlowAPI](https://github.com/laurentS/slowapi)
- **Dependency Management**: [uv](https://github.com/astral-sh/uv) & `pyproject.toml`

## 🛠️ Backend Features

1. **Scan Orchestration**: Drives various research modules (HIBP, GitHub, RansomLook, etc.).
2. **CVE System**: Monitors vulnerabilities in real-time via NVD (NIST) and OSV.dev feeds.
3. **Historical Persistence**: Storage of critical alerts (e.g., Ransomware `CyberFinding`) in the database for historical tracking.
4. **User Management**: Secure authentication, roles (Admin/Viewer), and MFA management.
5. **Report Generation**: Aggregates scan results into HTML, Markdown, or PDF reports.
6. **Webhooks**: Reception endpoint for external alerts (e.g., GitHub Secret Scanning).

## 📡 Main Endpoints

The API is documented via Swagger UI at `/docs` (in development mode).

- `/auth`: Authentication, token refresh, MFA verification.
- `/users`: User account and profile management.
- `/scans`: Manual triggering and history of domain scans.
- `/api/v1/dashboard`: Aggregated statistics for frontend charts.
- `/api/v1/cve`: Consultation and filtering of detected vulnerabilities.
- `/api/v1/ransomlook`: Ransomware group monitoring data.
- `/api/v1/intelligence`: Intelligence and persistent threat feeds (Ransomware, RSS).
- `/api/v1/settings`: Global configuration, OSINT API key management.
- `/webhooks`: Reception of external alerts.

## 💻 Local Installation (without Docker)

If you want to run the backend natively for development:

### 1. Prerequisites
- Python 3.12 installed.
- An active **PostgreSQL** instance (create a `breachradar` DB).
- An active **Redis** instance.

### 2. Environment Setup
```bash
# Go to the backend directory
cd backend

# Create the virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies in editable mode
pip install -e .[dev]
```

### 3. Configuration
Ensure you have a `.env` file at the project root (BreachRadar/) with the necessary variables (see `.env.example`).

### 4. Running
```bash
# Run the API with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The API will be accessible at [http://localhost:8000](http://localhost:8000).

## 🧪 Tests & Quality
```bash
# Run tests
pytest

# Type checking
mypy .

# Linting
ruff check .
```
