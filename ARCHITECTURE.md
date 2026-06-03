# BreachRadar Architecture

This document details the organization of the BreachRadar repository, the responsibilities of each module, the location of configuration files, and protocols dedicated to AI agents.

## 🏗️ Project Overview

BreachRadar is a cyber intelligence platform structured into three main pillars:
1.  **Backend (FastAPI)**: Collection engine (OSINT), data aggregation, and REST API.
2.  **Frontend (Next.js)**: Modern user interface for alert visualization and configuration management.
3.  **Third-Party Services (Docker)**: Stack including Redis, PostgreSQL, Tor, and RansomLook.

---

## 📁 Detailed Directory Structure

### 🔹 `/backend` — The Heart of the System
Contains all business logic, OSINT collectors, and the API.

*   `backend/app/main.py`: Entry point for the FastAPI application.
*   `backend/app/core/`: Global configuration (`config.py`), database connection (`database.py`), security (`security.py`), and source registries.
*   `backend/app/engine/`: Execution engine.
    *   `orchestrator.py`: Coordinates scans and collectors.
    *   `aggregator.py`: Merges and deduplicates results.
    *   `scheduler.py`: Manages scheduled tasks (protected by **Redis Distributed Lock** to avoid multi-worker conflicts).
*   `backend/app/clients/`: API clients for external sources (HIBP, IntelX, Dehashed, RansomLook, etc.).
*   `backend/app/models/`: SQL table definitions (SQLAlchemy), including the `CyberFinding` historical persistence for Ransomware alerts.
*   `backend/app/routers/`: REST API endpoints organized by domain (auth, scans, cve, dashboard).
*   `backend/app/schemas/`: Data validation models (Pydantic) for API requests/responses.
*   `backend/tests/`: Unit and integration test suite using `pytest`.

### 🔹 `/frontend` — The User Interface
Next.js application (App Router) developed in TypeScript.

*   `frontend/src/app/`: Structure of pages and layouts (Dashboard, Login, Admin).
*   `frontend/src/components/`: Reusable UI components (shadcn/ui, tables, charts).
*   `frontend/src/lib/`: Utilities, store management (Zustand/Context), and API client.
*   `frontend/messages/`: Translation files (**i18n**) in French and English.

### 🔹 `/ransomlook_config`
Contains specific scripts and configuration files for RansomLook integration (monitoring ransomware groups).
*   `start_local.sh`: Service startup script in Docker.
*   `patch_api.py` / `patch_redis.py`: Utility scripts to adjust RansomLook behavior.

### 🔹 `.github/workflows/` — Continuous Integration (CI/CD)
*   `ci.yml`: Automated security and quality pipeline (Ruff, Mypy, Bandit, NPM Audit, detect-secrets) executed on every Pull Request to block regressions and vulnerabilities.

### 🔹 `/security_audits`
Folder dedicated to security documentation and audit procedures.
*   `AUDIT_INSTRUCTIONS.md`: Guide for conducting security audits on the repo.
*   `TECH_STACK.md`: Detailed technical inventory and security status of components.

---

## ⚙️ Configuration

The project uses environment variables for its configuration.

| Type | File | Description |
| :--- | :--- | :--- |
| **Global** | `.env` | Environment variables (secrets, API keys, service URLs). See `.env.example`. |
| **Backend** | `backend/app/core/config.py` | Loading and validation of variables via Pydantic Settings. |
| **Docker** | `docker-compose.yml` | Container orchestration (ports, networks, volumes). |
| **Frontend** | `frontend/next.config.ts` | Next.js configuration (CSP, rewrites, security headers). |
| **Linting/Style** | `.pre-commit-config.yaml` | Pre-commit validation hooks (Ruff, MyPy). |

---

## 🤖 Artificial Intelligence (AI Agents)

The repository is optimized for collaboration with AI agents (Gemini, Claude, GPT). Several files and folders are dedicated to them:

*   **`AI_AGENT_GUIDE.md`** (Root): **Mandatory entry point.** Contains the mission, traceability protocols, and rules for handovers between sessions.
*   **`.gemini/`**: Specific folder for Gemini CLI.
    *   `.gemini/skills/`: Contains specialized instructions ("skills") allowing the AI to act with specific expertise in certain areas (e.g., `python-api-backend`, `nextjs-app-router`).
*   **`AI_AGENT_GUIDE.md`** replaces the old `AGENT.md` and `IA_CHANGE.md` files to centralize steering.

---

## 📈 Project Management and Tracking

*   **`ROADMAP.md`**: Contains the project's progress status, upcoming tasks, and the detailed **CHANGELOG** for each session.
*   **`PROJECT_SPECIFICATIONS.md`**: Reference document on initial functional and technical needs.
*   **`README.md`** (Root): General presentation and quick deployment instructions.
*   **`QUICKSTART.md`**: Step-by-step guide to launch the project in Docker or local development mode.
*   **`SECURITY_BEST-PRACTICE.md`**: Guide to security standards to follow during development.

---

## 🛠️ Maintenance Tools

*   **`Makefile`**: Shortcuts for common commands (build, tests, lint, clean).
*   **`scripts/`**: Miscellaneous utility scripts (e.g., `verify_sanitizer.py`).
*   **`reports/`**: Output folder for reports generated by the system (PDF/MD/HTML).
