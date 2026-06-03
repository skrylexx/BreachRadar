# AUDIT_INSTRUCTIONS — BreachRadar Security Audit

> ⚠️ Read `READ_BEFORE_RUN.md` before any execution.
> This file defines the scope, deliverables, and audit rules.
> The full technical description is in `TECH_STACK.md`.

***

## 0. Role & Stance

Act as a **Senior Cybersecurity Expert and DevSecOps Engineer**.
You are performing a **critical, exhaustive, and operational** security audit of the BreachRadar repository.
You make **no generalizations**: each finding cites the exact file, line, or code block concerned.
If an audit point presents no flaw, you **explicitly justify** why the configuration is considered safe.

***

## 1. Audit Scope

The audit covers **six pillars** in this descending order of priority:

### 1.1 — Authentication & Token Management

**Target Files:**

- `backend/app/routers/auth.py`
- `backend/app/core/security.py`
- `backend/app/core/redis.py`
- `backend/app/dependencies/` (auth.py, roles)

**Points to Analyze:**

- JWT Flow: creation, verification, Redis blacklist (logout), access/refresh token rotation.
- HS256 Algorithm: adequacy and risks (symmetric, shared secret).
- HttpOnly Cookies: `COOKIE_SECURE` conditional on `ENVIRONMENT=production` → behavior in dev.
- `COOKIE_SAMESITE = "lax"`: evaluation of CSRF protection in this context.
- Refresh token path restricted to `/auth/refresh`: verify effective implementation.
- MFA TOTP: endpoint `/auth/mfa/verify` returns `501 NOT_IMPLEMENTED` → absence of effective MFA.
- MFA setup `/auth/mfa/setup`: the secret is stored in `user.mfa_secret` without activation → risk of orphaned unencrypted secret in database.
- MFA challenge stored in Redis (`store_mfa_challenge`): TTL, link with user_id, resistance to brute-force.
- `password_length` stored in plain text in the User model → sensitive information.
- Constant-timing verification (dummy_hash): analyze real robustness.
- Password rotation management: `last_password_change` + `password_length` in DB.

### 1.2 — Backend FastAPI (Code & Dependencies)

**Target Files:**

- `backend/app/routers/scans.py`
- `backend/app/routers/webhooks.py`
- `backend/app/routers/users.py`
- `backend/app/routers/api_keys.py`
- `backend/app/core/config.py`
- `backend/app/core/init_db.py`
- `backend/app/engine/logic.py` + `scheduler.py`
- `backend/app/clients/` (external OSINT calls)
- `backend/pyproject.toml`

**Points to Analyze:**

- **RBAC / Broken Access Control**: `AdminUser` vs `ViewerUser` dependencies — verify that no sensitive endpoint uses only `ViewerUser` or no dependency at all.
- **Scan trigger** (`POST /scans/trigger`): `body.target_domain` is passed directly to `ScanManager.run_full_scan` — verify Pydantic domain validation and SSRF risks if this domain is used in outgoing HTTP requests.
- **GitHub Webhook** (`POST /webhooks/github`): conditional HMAC signature verification (`if secret_token`) — if `github_webhook_secret` is missing from settings, any POST is accepted without authentication.
- **`init_db.py`**: creation of initial admin from `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` — verify if recreated at each startup or protected by an idempotent condition.
- **`config.py`**: `lru_cache` on `get_settings()` — verify implications in case of env variable reloading.
- **`extra="ignore"`** in pydantic-settings — poorly named variables can pass silently without error.
- **Dependencies**: analyze known CVEs for versions pinned in `pyproject.toml` (python-jose 3.3.0, passlib 1.7.4, python-multipart, aiohttp, etc.).
- **`allow_headers=["*"]`** in CORSMiddleware with `allow_credentials=True`: evaluate CORS attack surface.
- **Logs / Information Leakage**: verify that API keys, tokens, and sensitive data are not logged in OSINT clients or the engine.

### 1.3 — Secrets Management

**Target Files:**

- `.env.example`
- `docker-compose.yml`
- `backend/app/core/config.py`

**Points to Analyze:**

- `UI_REDIS_PASSWORD` passed in the `redis-server --requirepass ${UI_REDIS_PASSWORD}` command — visible via `docker inspect` or `ps aux`.
- `NEXT_PUBLIC_API_URL` encoded in the static JS bundle at build-time (intentional but to be qualified).
- Absence of native Docker Secrets or Vault-like manager.
- OSINT API keys (Shodan, HIBP, IntelX...) transit through env variables — verify they are not exposed in API responses or logs.
- `initial_admin_password` loaded from env at startup — if the DB is already initialized, verify it is not rewritten or logged.

### 1.4 — Containerization (Docker & Docker Compose)

**Target Files:**

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `Dockerfile` (root — if present)

**Points to Analyze:**

- **Supply Chain**: `curl -LsSf https://astral.sh/uv/install.sh | sh` executed at build — absence of integrity check (hash/signature).
- **Unpinned Images**: `dperson/torproxy:latest` and `travishunting/ransomlook:latest` — `latest` tags without SHA256 digest.
- **UV_SYSTEM_PYTHON=1**: installs dependencies in system Python (no isolated venv) — implications in case of compromise.
- **`ENV HOSTNAME="0.0.0.0"`** in frontend runner — listens on all interfaces in the container (acceptable if port is bound to 127.0.0.1 on host side, but to be documented).
- **Absence of `read_only: true`** on container filesystems.
- **Absence of `cap_drop: ALL`** and seccomp/AppArmor profiles.
- **Bind mount `./reports:/app/reports`** — verify permissions and path traversal risks if report name is user-controlled.
- **uv installed via `/root/.cargo/bin`** then `USER brapi` — verify that non-root user cannot call uv to install packages.

### 1.5 — Frontend Next.js (Headers & Exposure)

**Target Files:**

- `frontend/next.config.ts`
- `frontend/package.json`
- `frontend/src/` (components, pages, API calls)

**Points to Analyze:**

- **CSP `unsafe-inline` + `unsafe-eval`** in `script-src` — invalidates most XSS protections offered by CSP.
- **`connect-src 'self' http://localhost:8000`** — hardcoded in HTTP (not HTTPS), unsuitable for real production deployment.
- **Absence of HSTS** (`Strict-Transport-Security`) in headers.
- **Absence of `Permissions-Policy`** header.
- **`js-cookie`** used on client side — verify that JWT tokens are not stored in cookies accessible via JS (must remain HttpOnly set by the backend).
- **`NEXT_PUBLIC_API_URL`** injected at build — verify no other sensitive variable follows this pattern.
- **npm Dependencies**: analyze known vulnerabilities in `next@15.1.3`, `react@19.0.0`, and Radix UI components.

### 1.6 — Business Critical Functions

**Target Files:**

- `backend/app/engine/logic.py` (ScanManager)
- `backend/app/engine/scheduler.py` (ScanScheduler)
- `backend/app/clients/` (HTTP clients to OSINT sources)
- `backend/app/notifications/engine.py`
- `backend/app/report/`

**Points to Analyze:**

- **SSRF (Server-Side Request Forgery)**: is the `target_domain` provided by the admin validated before being used in outgoing HTTP requests? Risk of pointing to internal resources (169.254.0.0/16, 10.0.0.0/8).
- **Injection in OSINT calls**: are search terms (`ransomlook_search_terms`, domain) sanitized before being interpolated into URLs or requests?
- **`ScanManager.run_full_scan`** launched in FastAPI `BackgroundTasks`: error management, timeout, isolation.
- **APScheduler Scheduler**: verify that the `_scan_callback` in `main.py` does not allow uncontrolled concurrent triggering.
- **Report Generation**: if filename or content integrates user data, verify injection risks (path traversal, Jinja2 template injection).
- **`NotificationEngine`**: verify that the webhook URL (`ransomlook_alert_webhook`) is validated before being called (SSRF).

***

## 2. Deliverable Format

### 2.1 — Executive Summary

At the top of the report, present the following summary block:

```
GLOBAL RISK SCORE: [Critical / High / Medium / Low]
─────────────────────────────────────
🔴 Critical   : X
🟠 High       : X
🟡 Medium     : X
🔵 Low        : X
✅ Compliant  : X
─────────────────────────────────────
Audited Commit: [SHA]
Audit Date    : [YYYY-MM-DD]
```

### 2.2 — Vulnerability Table

Present each finding as a Markdown table with the following columns:

| # | Severity | Pillar | Component / File | Flaw Description | PoC / Code Line | Immediate Remediation |
|---|----------|--------|------------------|------------------|-----------------|-----------------------|

**Severity Scale:**

- 🔴 **Critical** — remotely exploitable, direct impact on data confidentiality or integrity.
- 🟠 **High** — exploitable with conditions, significant impact.
- 🟡 **Medium** — exploitable in combination or with prior access.
- 🔵 **Low** — best practice not followed, limited impact.
- ✅ **Compliant** — point analyzed, configuration considered safe (with justification).

**Sorting Rule:** Sort the table by descending severity (Critical → Low → Compliant).

***

## 3. Post-Audit Action Plan (Roadmap)

Conclude with a prioritized roadmap in **three time horizons**.

### Horizon 1 — Immediate (< 7 days)

Blocking actions to be addressed before any production release.

Expected examples: enable HMAC webhook unconditionally, implement `/auth/mfa/verify`, pin Docker images with SHA256 digest.

### Horizon 2 — Short Term (< 30 days)

Structural hardening without critical urgency.

Expected examples: replace `curl | sh` with a versioned and verified binary, add HSTS, fix CSP, remove `unsafe-eval` and `unsafe-inline`.

### Horizon 3 — Medium Term (< 90 days)

Long-term security strategy.

Expected examples: CI/CD pipeline with Trivy + Bandit + OWASP Dependency-Check, Docker Secrets or HashiCorp Vault, DAST on staging, OSINT secret rotation policy, dependency CVE monitoring.

**For each roadmap action, specify:**

| Action | Effort | Impact | File(s) / Service(s) |
|--------|--------|--------|----------------------|
| Action Description | Low / Medium / High | Critical / High / Medium / Low | Concerned Files |

***

## 4. Execution Rules

1. **Read `TECH_STACK.md` in full** before starting — all versions and configurations are documented there.
2. **Do not generalize**: each finding must reference a specific file and line or code block.
3. **Cross-reference CVEs**: for each dependency listed in `pyproject.toml` and `package.json`, check for known CVEs at the audit date.
4. **Test logic, not just configuration**: analyze complete flows (e.g., login → MFA → token → logout) to detect business logic flaws.
5. **Report `TODO` and `NOT_IMPLEMENTED`** as findings in their own right (e.g., `/auth/mfa/verify` returns 501).
6. **Do not assume**: if information is missing from `TECH_STACK.md`, explicitly state it rather than making an unverified hypothesis.
