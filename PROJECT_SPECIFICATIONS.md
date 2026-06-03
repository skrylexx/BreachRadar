# WebUI + CLI Specifications — BreachRadar

## 1. Context and Objectives

BreachRadar is a data breach detection platform targeted at a domain (e.g., `@mydomain.com`), combining:
- a modern **WebUI** for security / governance teams,
- an **asynchronous backend engine** to orchestrate scans,
- and **strong integration with RansomLook** for early detection of ongoing ransomware campaigns.

Main Objectives:
- Offer a **dense but readable Web dashboard**, SOC / governance-oriented, not marketing.
- Allow analysts to **visualize the state of compromise over time**, by source and globally.
- Ensure **GDPR-by-design implementation**: zero exposure of secrets, neutral reports.
- Provide in parallel an **administration / integration CLI** (devops, CI, debug).

## 2. Functional Scope

This specification covers:
- the **WebUI** (Next.js frontend + FastAPI backend already present in the repo),
- the platform's **administration CLI** (Python command or entry point in the backend container).

Excluded (but described in other documents):
- full detail of each OSINT source,
- exhaustive description of internal models,
- very low-level documentation of RansomLook already present in `PROJECT_SPECIFICATIONS.md`.

## 3. Users and Roles

### 3.1 Personae

- **Admin / Security Manager**
  - Configures API keys, SMTP, RansomLook.
  - Manages users and roles.
  - Triggers manual scans if needed.
  - Consumes PDF reports for governance committees.

- **Viewer / SOC Analyst**
  - Consults the dashboard and history.
  - Navigates through reports.
  - Exports reports (PDF, possibly CSV).
  - Does not modify any sensitive configuration.

### 3.2 RBAC (Rules)

- Admin: full access, including management of API keys, SMTP, users, scan settings.
- Viewer: read-only access to dashboards, reports, history; export only.

## 4. Architecture & Technical Stack

### 4.1 Overview

Current stack to be formalized:

- **Frontend WebUI**
  - Next.js 15 (App Router) + TypeScript.
  - Tailwind CSS + Shadcn/UI for components and theme.
  - Dark theme by default, with dark/light switch.
  - i18n: English (default) + French.

- **Backend Web / Engine**
  - FastAPI (Python 3.12).
  - Asynchronous scan engine (HTTPX + asyncio).
  - APScheduler integrated into the backend for weekly scans.

- **Persistence & Infra**
  - PostgreSQL 16:
    - storage of user accounts, roles, application sessions (if needed),
    - storage of **sanitized** scan results (no raw sensitive data).
  - Redis 7: cache, session management, and rate limiting.
  - RansomLook:
    - either self-hosted Docker instance on internal network, without API key,
    - or use of the SaaS API `https://www.ransomlook.io/api` (API key in `Authorization` header).

### 4.2 RansomLook Modes (Local / SaaS)

Two RansomLook integration modes are supported by the platform:

- **Local Mode (default)**
  - The RansomLook Docker stack (`ransomlook-redis`, `ransomlook-tor`, `ransomlook-app`) is deployed with BreachRadar.
  - The API is exposed internally only (`http://ransomlook-app:8888` on the Docker network, and `127.0.0.1:8888` on the host side).
  - No authentication header is required.
  - Main variables:
    - `RANSOMLOOK_MODE=local`
    - `RANSOMLOOK_LOCAL_URL=http://ransomlook-app:8888`

- **SaaS Mode**
  - No RansomLook containers are launched.
  - The hosted API is called via `https://www.ransomlook.io/api`.
  - An API key is provided in the RansomLook user account and injected into the environment.
  - The HTTP client automatically adds the `Authorization: <RANSOMLOOK_SAAS_API_KEY>` header.
  - Main variables:
    - `RANSOMLOOK_MODE=saas`
    - `RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api`
    - `RANSOMLOOK_SAAS_API_KEY=<key provided by RansomLook>`

In both cases, the search terms used to query RansomLook are built from:
- `TARGET_DOMAIN`,
- a possible domain root (e.g., `mydomain` for `mydomain.com`),
- `RANSOMLOOK_SEARCH_TERMS` (CSV list of commercial names, subsidiaries, etc.).

### 4.3 Docker Architecture

- `frontend`: Next.js (port 3000).
- `backend`: FastAPI + asynchronous engine (internal port, e.g., 8000).
- `db`: Postgres.
- `redis`: cache, rate limiting.
- `ransomlook-*`: RansomLook stack (redis/tor/app) if **local mode**.
- `mail`: external SMTP or mail service according to configuration.

Containers are orchestrated by a **single docker-compose** that exposes only:
- the frontend on `http://localhost:3000`,
- the backend API on `127.0.0.1:8000`.

RansomLook must **never** be exposed on 0.0.0.0; only on the internal Docker network or on `127.0.0.1`.

## 5. WebUI — Design Principles & Identity

### 5.1 General Style

- **Cyber / governance** theme, not marketing.
- Dark mode by default, Shadcn/UI inspired palette:
  - Background: `#09090b`.
  - Surfaces (cards, modals): `#18181b`.
  - "Radar" accent: cyan/indigo blue `#38bdf8`.
- Severity color codes:
  - Red (CRITICAL) / Orange (HIGH) / Yellow (MEDIUM) / Blue or grey (LOW).

### 5.2 Typography

- General UI: **Inter**.
- Technical data (hashes, emails, logs, indicators): **JetBrains Mono**.

### 5.3 Layout

- **Slim sidebar** on the left, icons only:
  - Dashboard, Scans, API Keys, Users, Changelog/Updates.
- Header:
  - Language switch (EN / FR).
  - Dark mode switch.
  - User profile (dropdown menu: profile, MFA, logout).
- "SOC dashboard" type central content:
  - Heatmap / global evolution chart at the top.
  - API status cards.
  - Data breach and alert tables at the bottom.

### 5.4 "Radar" Identity

- Discrete visual radar element:
  - on the landing (main dashboard),
  - and as a loading animation when launching a scan (radar-type spinner).

## 6. WebUI — Pages and Flows

### 6.1 Landing / Dashboard

Objective: synthetic view of the domain's security state.

Minimal content:

- **Heatmap / global evolution chart** (12 months by default, with filters 7d / 1 month / 6 months / 12 months)
  - X-axis: time.
  - Y-axis: number of "reported issues" (findings) across all tools.
  - Representation in bars or NinjaOne-type line.

- **Source / Connector status cards**:
  - HIBP, LeakCheck, Dehashed, GitHub, URLScan, OTX, RansomLook, etc.
  - Each card displays: source name, status (✅ / ⚠️ / ❌), date of last success, severity badge if RansomLook signals a CRITICAL alert.
  - Colored border or "sidebar" (green/red) for active state.

- **"Ransomware / RansomLook" block in case of alert**:
  - summary of the last alert (group, detection date, claimed size, status),
  - CTA to the detailed "Ransomware Alerts" page.

- **Summary of the last weekly scans**:
  - scan table (date, duration, number of findings, global severity),
  - timestamps without seconds (e.g., `2026-05-05 10:03`).

- Quick access:
  - links to each tool's page,
  - link to the global "Reports" page.

### 6.2 Tool Pages

One page per source / source family (e.g., "HIBP & Breaches", "GitHub & GitLab", "RansomLook").

For each page:
- temporal filter (7d / 1 month / 6 months / 12 months / "all time"),
- **specific evolution chart**:
  - X-axis: time.
  - Y-axis: number of findings for this source only.
- table of recent findings:
  - columns: date, type (email / domain / ransomware), severity, source, summary,
  - colored severity badges,
  - server-side pagination.
- "Relaunch a scan for this source" button (Admin only).

### 6.3 Reports Page

- list of **scan reports** (weekly + manual):
  - date, domain, global severity, number of compromised emails, presence or absence of RansomLook alert.
- possible actions:
  - **Export report as PDF**,
  - (optional) JSON / CSV export.
- "Generate a global report for period X" button: aggregation of multiple scans.

### 6.4 Ransomware Alerts Page (RansomLook)

- "Instance State" section: URL used, number of tracked groups, number of posts, last update.
- list of alerts: group (LockBit, BlackCat, etc.), victim/victim_name, country, sector, claim_size, status (LISTED / PUBLISHED), discovery / publication date.
- actions: filter by group, country, sector, status; access the report containing the alert.
- **Note**: never any .onion URLs in the interface, only an "URL available in secure logs" indicator.

### 6.5 Administration

Accessible only to Admin.

Sections:

- **Users & Roles**:
  - creation / deletion of users (email + password + role),
  - email password reset, MFA management (activation, reset),
  - password policy: Admin min 16 characters, Viewer min 12 characters, rotation every 6 months with blocking if not renewed.

- **API Keys & Integrations**:
  - form to configure: TARGET_DOMAIN, HIBP_API_KEY, GITHUB_TOKEN, URLSCAN_API_KEY, OTX_API_KEY, LEAKCHECK_API_KEY, DEHASHED_API_KEY, etc.,
  - RansomLook parameters (local vs SaaS mode + API key if SaaS),
  - visual indicator if the key is present (bool), without ever showing it in clear text,
  - "Test this source" button (health ping).

- **SMTP / Mail Configuration**:
  - host, port, TLS/SSL, user/password, from, reply-to,
  - "Send a test email" button.

- **Scheduling**:
  - activation/deactivation of the weekly cron,
  - configurable cron expression (with validation),
  - display of the next scheduled run.

- **Audit Trail**:
  - list of admin actions: login, key modification, role change, scan relaunch, report export, etc.,
  - filtering by user / action type.

### 6.6 "Changelog / Updates" Page

- List of major platform developments (version, date, summary).
- Accessible from the bottom of the menu.

## 7. WebUI — i18n

- Languages: **EN** by default, **FR**.
- Language selection button in the header (globe icon + abbreviation).
- Storage of preference in cookie/localStorage, fallback on Accept-Language header.
- Externalized texts (`en.json`, `fr.json` files on the frontend side).

## 8. Administration CLI (Command Line Interface)

> **Administration / integration** CLI usable in the backend container. It targets ops/dev, not end users.

### 8.1 CLI Objectives

- Provide script-friendly commands to:
  - trigger a full or specific scan,
  - check the health of sources (including RansomLook),
  - list the latest scans and their status,
  - generate a report (PDF) from the scan ID.

### 8.2 CLI Stack

- Python implementation (Typer or Click) in `backend/app/main_cli.py` for example.
- Typical execution:

```bash
# In the backend container
docker compose exec backend python -m app.main_cli scan --full
```

### 8.3 Minimal Commands

- `scan full`
  - launches a full scan with all enabled sources.
  - options: `--async` (immediate return / background job), `--tag <label>`.

- `scan tool --name <source>`
  - launches a scan limited to a source (e.g., `hibp`, `github`, `ransomlook`).

- `ransomlook health`
  - checks the health of the RansomLook instance (local or SaaS).

- `ransomlook check --domain <domain>`
  - forces a domain check on RansomLook.

- `report generate --scan-id <id> --format pdf`
  - generates a PDF report for an existing scan, stored in `reports/`.

- `scans list --limit N`
  - lists the N latest scans (id, date, duration, global severity).

## 9. Security & Compliance

- **Web**:
  - CSRF on forms.
  - Rate limiting on `/auth/login`, `/scan/*`, `/reports/export`.
  - Strict input validation (Pydantic on the backend side).

- **Passwords and MFA**:
  - policies described above (length, rotation, blocking),
  - TOTP secret stored encrypted (e.g., Fernet/Key Management).

- **Data and GDPR**:
  - no raw sensitive data (password, hash, API key, .onion URL) in the database,
  - only indicators: booleans (has_password, has_hash…), breach metadata, etc.,
  - RansomLook: data already public, but we prevent direct exposure of .onion URLs (only advanced admins can see them in secure logs outside the WebUI).

## 10. Deployment & Configuration

- **Single `.env` file** for:
  - WebUI parameters (JWT, initial admin, DB, Redis),
  - OSINT API keys,
  - RansomLook configuration (local vs SaaS mode + URL + API key).

- **docker-compose**:
  - a `docker compose up -d` must start the full WebUI stack, including RansomLook (local mode),
  - in RansomLook SaaS mode, no RansomLook container is launched, only `RANSOMLOOK_SAAS_API_URL` + `RANSOMLOOK_SAAS_API_KEY` are used.
