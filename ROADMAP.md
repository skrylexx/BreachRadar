# ROADMAP — BreachRadar

> Structured logbook — updated at every AI or human iteration.
> **Handoff protocol**: Read this file + README.md + CYBER_SECURITY_CHECKLIST.md before any contribution.

---

## Global Progress

```
Phase 1 — MVP         [██████████] 100%
Phase 2               [██████████] 100%
Phase 3               [██████████] 100%
Phase 4 — WebUI       [██████████] 100%
Phase 5 — Hardening   [██████████] 100%

── Frontend (TODO.md) ──────────────────
Phase 0 — Foundations [██████████] 100%
Phase 1 — Dashboard   [██████████] 100%
Phase 2 — Tools       [██████████] 100%
Phase 3 — Reports     [██████████] 100%
Phase 4 — Ransomware  [██████████] 100%
Phase 5 — Admin       [██████████] 100%

── Backend Implementation ──────────────
Phase 1 — CVE Engine  [██████████] 100%
Phase 2 — Security    [██████████] 100%
Phase 3 — Settings    [██████████] 100%
Phase 4 — Reports     [██████████] 100%
Phase 5 — Validation  [██████████] 100%
```

---

## Global Vision

### Phase 5 — Hardening (100%)
- [x] Fernet encryption of API keys in DB
- [x] Dynamic management of demonstration data (Mock Mode)
- [x] Centralization of System Settings in the database
- [x] Full security flow (MFA + Password change)
- [x] Global consolidation of scan reports
- [x] Correction and stabilization of Docker build (Full Stack)
- [x] Activation of automatic CVE polling via APScheduler
- [x] Strengthening of OSINT clients (Dynamic rate-limiting, HTTP error handling)
- [x] Async test coverage for CVE engine (API Mocking)
- [x] Automated security audit (Bandit, Semgrep) and fix of Jinja2 vulnerabilities (XSS)
- [x] Complete technical documentation (Backend/Frontend READMEs + Local Setup)

---

## CHANGELOG

### Iteration 42 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Fix of Docker API startup error (missing database columns) and environment clarification.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/core/init_db.py` | Modification | Implementation of automatic schema synchronization (`ALTER TABLE ... ADD COLUMN IF NOT EXISTS`). |
| `ROADMAP.md` | Modification | Iteration 42 logging and next agent update. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #14. |

#### ✅ Fixes & Maintenance
- **Database Schema Sync**: Automated addition of missing columns (`token_version`, MFA fields, etc.) in the `users` table to support upgrades from older versions without requiring a full database reset.
- **MOCK_MODE clarification**: Explicit identification of the correct environment variable for demonstration mode.

---

### Iteration 41 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: v0.4.1 Update (RBAC Hardening) and CI/CD pipeline audit.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `frontend/src/app/(dashboard)/changelog/page.tsx` | Modification | Added v0.4.1 version. |
| `ROADMAP.md` | Modification | Iteration 41 logging. |

#### ✅ Evolutions
- **Version v0.4.1**: RBAC controls hardening and input securing.
- **CI/CD Audit**: Debugging and consistency verification of the continuous integration pipeline (ongoing).

---

### Iteration 40 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Finalization of Ransomware persistence, RBAC reinforcement, and v0.4.0 update.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/core/init_db.py` | Modification | Initial admin securing (MFA/Sessions Reset). |
| `backend/app/dependencies/auth.py` | Modification | `require_admin` check hardening (RBAC fix). |
| `backend/app/engine/logic.py` | Modification | Implementation of RansomLook findings persistence in the database. |
| `frontend/src/app/(dashboard)/changelog/page.tsx` | Modification | Publication of version v0.4.0. |
| `ROADMAP.md` | Modification | Iteration 40 logging. |

#### ✅ Maintenance & Evolutions
- **Ransomware Persistence**: Positive detections are now saved in the `cyber_findings` table, allowing for historical tracking and visibility in the intelligence flow.
- **RBAC Fix**: Correction of "insufficient" permission issues for the administrator when triggering scans.
- **Admin Recovery**: The initial administrator is now created with healthy security settings (MFA disabled by default) to avoid any blocking during the first launch.
- **Version v0.4.0**: Official move to v0.4.0 including i18n and security audits.

---

### Iteration 39 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Resolution of Docker image resolution error, fix of "Black Screen" (CSP), reliability improvement of Backend startup (Race Condition), and fix of the logout flow.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `docker-compose.yml` | Modification | Update of SHA256 digests for third-party images. |
| `frontend/next.config.ts` | Modification | CSP relaxation (`unsafe-inline`, `unsafe-eval`) to allow Next.js hydration. |
| `backend/app/main.py` | Modification | Added a Redis lock for the Scheduler (multi-worker singleton). |
| `backend/app/core/init_db.py` | Modification | Implementation of a robust Redis lock with retries for DB initialization. |
| `backend/app/dependencies/auth.py` | Modification | Improved RBAC error messages to facilitate debugging. |
| `frontend/src/components/layout/Header.tsx` | Modification | Fix of logout URL and dynamic admin email fetch. |
| `ROADMAP.md` | Modification | Iteration 39 logging. |

#### ✅ Maintenance & Stability
- **Docker Image Fix**: Fix of blocking SHA256 digests.
- **CSP Fix**: Resolution of the black screen.
- **Backend Startup**: Removal of `IntegrityError` on Enums via robust distributed locking.
- **RBAC & Auth**: Fix of logout (404) and improvement of permission feedback.
- **UX**: Email in the header is now retrieved from the actual session.

---

### Iteration 38 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Creation of a Gemini CI/CD skill, reinforcement of the quality pipeline, and achieving "Zero Defects" (Tests & Typing).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `.gemini/skills/cicd-expert/` | New | CI/CD skill folder (SKILL.md, references). |
| `.github/workflows/ci.yml` | Modification | Activation and configuration of `mypy`, `bandit`, and move to Node 22. |
| `backend/pyproject.toml` | Modification | Added `bandit`, optimized `ruff` and `mypy` configuration, fixed `bcrypt` version. |
| `backend/app/core/config.py` | Modification | Hardening of `Settings` (robust defaults, env validation) and Fernet fix. |
| `backend/tests/conftest.py` | Modification | Redesign of the fixtures system (global Mocks, auto cleanup of overrides). |
| `backend/tests/*.py` | Modification | Update of the test suite for compatibility with strict typing (datetime). |
| `frontend/.eslintrc.json` | New | Standard ESLint configuration to block fatal errors in CI build. |
| `ROADMAP.md` | Modification | Full iteration 38 logging. |

#### ✅ Quality & Robustness (100%)
- **Zero Mypy Errors**: Correction of 135 initial errors, including complex Liskov substitution principle violations.
- **79/79 Tests PASSED**: Stabilization of the backend test suite with total database isolation.
- **Green CI Pipeline**: Full automation (SCA, Secrets, Ruff, Bandit, Mypy, Tests, Docker Build).
- **AI Expertise**: Installation of the `cicd-expert` skill for future DevOps maintenance.

---

### Iteration 37 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Implementation of a GitHub Actions CI/CD pipeline for security and quality test automation.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `.github/workflows/ci.yml` | New | GitHub Actions pipeline running security audits, backend tests, frontend build, and Docker verification. |
| `ROADMAP.md` | Modification | Added iteration 37. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #11. |

#### ✅ CI/CD Automations
- **Security Audit**: Secret detection, NPM vulnerability scan, and pip-audit.
- **Backend Quality**: Ruff linting, unit tests, and asynchronous security tests.
- **Frontend Quality**: ESLint linting and Next.js build verification (production ready).
- **Infrastructure**: Systematic verification of Docker API and UI image builds.

---

### Iteration 36 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Full implementation of internationalization (FR/EN) on the frontend.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `frontend/messages/en.json` | Modification | Added all translation keys for Dashboard, Auth, MFA, Profile, Intelligence/Monitoring, and Scans. |
| `frontend/messages/fr.json` | Modification | Contextual French translation of the entire interface. |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Internationalization of the Dashboard (Server Component). |
| `frontend/src/components/layout/Header.tsx` | Modification | Translation of page titles, user menus, and language selector. |
| `frontend/src/app/(auth)/login/page.tsx` | Modification | Full translation of the login flow and error messages. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Modification | Translation of the MFA flow (TOTP and backup codes). |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Translation of profile management, password change, and MFA activation. |
| `frontend/src/app/(dashboard)/intelligence/page.tsx` | Modification | Translation of digital intelligence/monitoring and dynamic date locale management. |
| `frontend/src/app/(dashboard)/scans/page.tsx` | Modification | Translation of scan history. |
| `frontend/src/app/(dashboard)/reports/page.tsx` | Modification | Translation of report management and exports. |

#### ✅ i18n Results
- **Coverage**: The entire critical user flow (Login -> Dashboard -> Profile) is now translated.
- **Quality**: Use of adapted business terms (e.g., "Findings", "Intelligence/Monitoring").
- **Localization**: Dates, durations, and number formats respect FR and EN standards.

---

### Iteration 35 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Full execution of the security audit and application hardening (Phases 1 to 4).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/Dockerfile` | Modification | Base image SHA256 pinning + Secure UV installation (COPY from image). |
| `frontend/Dockerfile` | Modification | Base image SHA256 pinning. |
| `docker-compose.yml` | Modification | Pinning of all third-party images (Redis, Postgres, Tor, RansomLook) + Hardening (cap_drop, no-new-privileges). |
| `backend/app/schemas/scan.py` | Modification | Added strict `target_domain` validation to prevent SSRF. |
| `backend/app/routers/settings.py` | Modification | Restriction of `/settings/general` to administrators only. |
| `backend/app/routers/auth.py` | Modification | Correction of `refresh_token` cookie paths for proper isolation. |
| `frontend/next.config.ts` | Modification | CSP hardening (removal of unsafe-*) + Added HSTS and Permissions-Policy. |
| `TODO.md` | Modification | Progress status update (all phases completed). |

#### ✅ Audit Results
- **Supply Chain**: Docker images locked by digest, no more `curl | sh`.
- **RBAC**: Sensitive endpoints strictly protected by `AdminUser`.
- **Pentest**: Reinforced input validation, full MFA protection with brute-force protection.
- **Front-Back Comm**: Secure cookies and hardened HTTP headers.

---

### Iteration 34 — 2026-06-01 (Gemini CLI)

**Iteration Objective**: Initialization of the full security roadmap and test strategy preparation.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `TODO.md` | Modification | Full replacement by a 4-phase security roadmap (Audit, Code/Pentest, RBAC, Front-Back Comm). |
| `ROADMAP.md` | Modification | Progress status update and addition of iteration 34. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #9. |

#### ✅ Security Strategy
- [x] **Project Immersion**: Reading and analysis of the architecture, agent guide, and security best practices.
- [x] **Skill Activation**: Use of the `senior-webapp-cyber-auditor` skill to guide future audits.
- [x] **Security Roadmap**: Creation of a detailed action plan in `TODO.md` to secure the application before going live.
- [x] **Audit Pillars**: Integration of permission checks (RBAC), application pentest, and communication hardening.

---

### Iteration 33 — 2026-05-23 (Gemini CLI)

**Iteration Objective**: Full audit of versions and dependency security (SCA).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `PROCEDURE_CHECKS.md` | New | Reusable guide for future version audits. |
| `TODO.md` | Modification | Definition of security audit tasks. |
| `security_audits/TECH_STACK.md` | Modification | Synchronization of real versions (Runtimes + Packages). |

#### ✅ Security Audit (SCA)
- [x] **Backend Audit**: Detection of 6 vulnerabilities (`idna`, `urllib3`, `pip`). Real Python version: 3.14.3.
- [x] **Frontend Audit**: Detection of 6 vulnerabilities, including one **CRITICAL** on `Next.js 15.1.3` (RCE, SSRF, Cache Poisoning).
- [x] **Drift Analysis**: Frontend frameworks (`Next.js`, `React`, `Tailwind`) identified as having a significant lag behind the latest stable versions.
- [x] **Documentation**: Creation of the standard verification procedure.

---

### Iteration 32 — 2026-05-23 (Gemini CLI)

**Iteration Objective**: Implementation of the Digital Intelligence & Cyber Monitoring engine.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/engine/intelligence_monitor.py` | New | Global monitoring engine (RSS, GitHub, Pastebin, Telegram). |
| `backend/app/routers/intelligence.py` | New | REST API for monitoring flow management. |
| `frontend/src/app/(dashboard)/intelligence/page.tsx` | New | Real-time "Feed" view with advanced filters. |
| `backend/app/models/finding.py` | Modification | Generic and flexible `CyberFinding` model (JSONB). |
| `backend/app/notifications/engine.py` | Modification | Real-time alerting for critical threats. |

#### ✅ Intelligence & Monitoring
- [x] **RSS/Atom Engine**: Redirection support and 403 bypass (User-Agent).
- [x] **GitHub Connector**: Automated monitoring of domain mentions.
- [x] **Alert System**: Immediate notifications (Webhook/Email) for `CRITICAL` findings.
- [x] **UI Experience**: Real-time flow, strict deduplication, and triage by status (read/unread).
- [x] **Sources**: Integration of BleepingComputer, The Hacker News, CERT-FR, CISA, and IT-Connect.

---

### Iteration 31 — 2026-05-23 (Gemini CLI)

**Iteration Objective**: Stack maintenance and MFA flow redesign (UX + Resilience).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `SQL Migration` | Fix | Alignment of the `users` table (MFA columns + Session revocation). |
| `backend/app/routers/auth.py` | Fix/Feature | Backup codes management, forced MFA reset after recovery, and full User object return. |
| `frontend/src/lib/api.ts` | Fix | Added `suppressRedirect` to avoid premature logouts during token refresh. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Feature | Recovery mode (Backup codes), auto-focus, and "Device not available" link. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Fix/UX | Local user state update and auto-focus in dialogs. |

#### ✅ Maintenance & Stability
- [x] **Database Sync**: PostgreSQL schema synchronization.
- [x] **MFA Flow Fix**: Fix of immediate logout via local state update and removal of untimely 401 redirections.
- [x] **Recovery Mode**: Full implementation of the recovery flow (Backup Codes).
- [x] **UX Improvements**: Auto-focus on all security fields and fluid navigation.
- [x] **Validation**: All Docker services are `healthy`.

---

### Iteration 30 — 2026-05-22 (Gemini CLI)

**Iteration Objective**: Security Hardening of the MFA implementation.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/models/user.py` | Modification | Added `token_version` for session revocation and `mfa_backup_codes` (JSON). |
| `backend/app/core/security.py` | Modification | Implementation of deterministic `Fernet` encryption and backup codes generation. |
| `backend/app/core/redis.py` | Modification | Added helpers for MFA failure tracking (Brute-force protection). |
| `backend/app/routers/auth.py` | Modification | Encryption at-rest, lockout enforcement (5 attempts), session invalidation, backup codes verification. |
| `backend/app/routers/users.py` | Modification | Session invalidation during admin action on MFA. |
| `backend/app/dependencies/auth.py` | Modification | `token_version` verification to prohibit revoked sessions. |
| `backend/app/schemas/auth.py` | Modification | Support for backup codes in the verification schema. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Added backup codes download step during MFA setup. |
| `backend/tests/test_mfa_ratelimit.py` | Creation | Isolated test to validate account lockout. |

#### ✅ Security Hardening (Phase 4)
- [x] **Encryption at Rest**: MFA secrets encrypted in the database.
- [x] **Session Revocation**: Immediate invalidation of tokens during a security change (MFA/Password).
- [x] **Account Lockout**: Anti brute-force protection (15min blocking after 5 TOTP failures).
- [x] **Backup & Recovery**: Generation, hashed storage, and use of 10 single-use backup codes.
- [x] Functional tests validated (10/10 passed).

---

### Iteration 29 — 2026-05-22 (Gemini CLI)

**Iteration Objective**: Implementation of User Self-Service MFA.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/routers/auth.py` | Modification | Added `mfa/disable` endpoint with TOTP verification. |
| `frontend/src/lib/api.ts` | Modification | Added `mfaDisable` method. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Added MFA deactivation button and dialog with `mfa_required` case management. |
| `backend/tests/test_mfa_functional.py` | Modification | Added MFA deactivation tests (Success/Failure). |

#### ✅ User Self-Service (Phase 3)
- [x] Backend: Secure deactivation by the user.
- [x] Frontend: Management interface in the profile.
- [x] Security: Deactivation blocking if MFA mandatory (admin).
- [x] Functional tests validated (6/6 passed).

---

### Iteration 28 — 2026-05-22 (Gemini CLI)

**Iteration Objective**: Implementation of Admin steering of MFA.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/models/user.py` | Modification | Added `mfa_required` column. |
| `backend/app/routers/users.py` | Modification | Added `reset-mfa` and `require-mfa` endpoints with audit logs. |
| `backend/app/routers/auth.py` | Modification | MFA mandatory enforcement during login. |
| `backend/app/schemas/user.py` | Modification | `mfa_required` exposure via `UserRead` API. |
| `frontend/src/lib/api.ts` | Modification | Integration of new `resetMfa` and `requireMfa` methods. |
| `frontend/src/app/(dashboard)/admin/users/client.tsx` | Modification | SOC table update: MFA columns and actions. |
| `backend/tests/test_admin_mfa.py` | Creation | Functional tests validating MFA reset and mandate. |

#### ✅ Admin MFA Management (Phase 2)
- [x] Backend: Operational management endpoints.
- [x] Frontend: Synchronized Admin Dashboard.
- [x] Security: Prohibited from resetting own MFA.
- [x] Functional tests validated (3/3 passed).

---

### Iteration 27 — 2026-05-22 (Gemini CLI)

**Iteration Objective**: Full implementation of the MFA verification flow (Login -> Challenge -> Verify).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/core/redis.py` | Modification | Optimization of MFA challenges storage (O(1) lookup via token). |
| `backend/app/routers/auth.py` | Modification | Refactoring of `mfa_verify` to use the new Redis lookup and added audit logs. |
| `frontend/src/lib/api.ts` | Modification | Alignment of `totp_code` parameter with backend schema. |
| `frontend/src/middleware.ts` | Modification | Authorization of access to `/mfa` without active session. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Creation | MFA verification page with SOC-radar design and error management. |
| `backend/tests/test_mfa_functional.py` | Creation | Automated functional tests of the full MFA flow. |

#### Technical Decisions

1. **Redis Efficiency**: Key/Value pair inversion in Redis (`mfa_challenge:{token} -> user_id`) to remove costly linear scans during verification.
2. **Design Continuity**: Reuse of components and SVG radar background from the login page for a fluid user experience.
3. **Security by Audit**: Systematic traceability of MFA attempts (success/failure) in SQLAlchemy audit logs.

#### ✅ MFA Flow (Phase 1)
- [x] Backend optimization (Redis + Router).
- [x] Frontend middleware updated.
- [x] `/mfa` page operational.
- [x] Functional tests validated (3/3 passed).

---

### Iteration 26 — 2026-05-21 (Gemini CLI)

**Iteration Objective**: Detailed planning and preparation for MFA improvements.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `TODO.md` | Creation | Detailed roadmap for MFA improvements (Login flow, Admin management, Security hardening). |

#### Technical Decisions

1. **Roadmap Approach**: Before implementing complex changes (DB migration, new routes), exhaustive planning was carried out in `TODO.md` to cover Backend, Frontend, and Security aspects.
2. **Verification Prioritization**: Identification of a flaw in the current flow (missing `/mfa` page and blocking middleware) which will be the first technical task.

#### ✅ MFA Planning
- [x] Creation of the full MFA `TODO.md`.
- [x] Definition of security hardening missions.
- [x] Push to `feat/mfa` branch.

---

### Iteration 25 — 2026-05-21 (Gemini CLI)

**Iteration Objective**: Restoration and population of data for the local RansomLook connector.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `docker-compose.yml` | Modification | Update of `ransomlook-app` healthcheck to use `wget` (curl absent from image). |

#### Technical Decisions

1. **Proactive Maintenance**: Manual cleaning of the RansomLook Redis database (DB 0, 2) to eliminate data corruption causing scraper crashes.
2. **Data Hydration**: Importing over 16,000 entries from the RansomWatch project to ensure the local instance is immediately useful without waiting for a full scraping cycle.
3. **Target Validation**: Manual verification that the search on the target domain (`olipes.com`) now returns consistent results via the internal API.

#### ✅ RansomLook
- [x] Fix of scraper crash (Redis flush).
- [x] Massive data import (16k+ victims).
- [x] Docker healthcheck fix.
- [x] Functional verification of victim search.

---

### Iteration 24 — 2026-05-19 (Gemini CLI)

**Iteration Objective**: Verification and reliability improvement of the RansomLook connection.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/models/ransom.py` | Modification | Added `mode` field to the `RansomStats` model. |
| `backend/app/clients/ransomlook.py` | Modification | Population of the `mode` field during healthcheck. |
| `frontend/src/app/(dashboard)/alerts/ransomware/client.tsx` | Modification | Correction of `last_updated` -> `last_update` field name to match backend. |

#### Technical Decisions

1. **End-to-End Validation**: Successful connectivity test between the backend client and the local RansomLook Docker instance.
2. **API/UI Harmonization**: Correction of a naming divergence on status metadata to ensure statistics display in the WebUI.

#### ✅ RansomLook Verification
- [x] RansomLook stack operational (Tor + Redis + App).
- [x] Backend client validated via test script (Healthy: True).
- [x] UI display fixed for statistics.
- [x] **Full SaaS Support**: SaaS API key is now retrieved from the database (Admin UI) if absent from `.env`.
- [x] **Engine Fix**: Fix of `ScanManager` crash during RansomLook initialization.
- [x] **Dashboard Status**: RansomLook status in the dashboard now takes into account keys configured via the Web interface.

---

### Iteration 23 — 2026-05-18 (Gemini CLI)

**Iteration Objective**: Documentation of the project's global architecture.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `ARCHITECTURE.md` | Creation | Detailed document explaining the directory structure, configurations, and the role of AI/Changelog files. |
| `ROADMAP.md` | Modification | Added iteration 23. |

#### Technical Decisions

1. **Knowledge Centralization**: `ARCHITECTURE.md` becomes the source of truth for understanding the physical and logical organization of the repository, complementing `AI_AGENT_GUIDE.md` which focuses on the workflow.

#### ✅ Documentation
- [x] Global architecture documented in `ARCHITECTURE.md`.

---

### Iteration 22 — 2026-05-18 (Gemini CLI)

**Iteration Objective**: Technical documentation generation and local launch guide.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `README.md` | Modification | Logo size reduction via `img` HTML tag. |
| `backend/README.md` | Modification | Added tech stack, utilities, endpoints, and local installation guide (venv). |
| `frontend/README.md` | Creation | Added tech stack, utilities, and local installation guide (npm). |
| `QUICKSTART.md` | Modification | Merging of Docker and Local Setup guides for quick startup. |
| `ROADMAP.md` | Modification | Phase 5 marked as 100% completed. |

#### Technical Decisions

1. **Dual-Path Setup**: The project now officially supports two launch modes: Docker (production/iso) and Local (rapid development).
2. **Docs Isolation**: Each component (backend/frontend) now has its own README detailing its specific stack, facilitating the onboarding of new developers or AI agents.

#### ✅ Phase 5.5 — Completed Tasks
- [x] Backend & Frontend technical documentation generated.
- [x] Unified and clarified Quickstart guide.

---

### Iteration 21 — 2026-05-17 (Gemini CLI)

**Iteration Objective**: Automated security audit and rendering vulnerability fixes.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/notifications/engine.py` | Modification | Activation of Jinja2 autoescape to prevent XSS injections in alerts. |
| `backend/app/report/engine.py` | Modification | Activation of Jinja2 autoescape for HTML/PDF reports. |
| `backend/app/clients/hibp.py` | Modification | Explicit exclusion (`nosec`/`nosemgrep`) of SHA1 hash for HIBP (security false positive). |
| `TODO.md` | Modification | Phase 5.3 marked as completed. |

#### Technical Decisions

1. **XSS Mitigation**: Activating `autoescape` in Jinja2 ensures that any dynamic content (CVE descriptions, ransomware victim names) is neutralized before being rendered in HTML.
2. **False Positive Management**: "Weak" algorithms like SHA1 are maintained only where required by third-party APIs (HIBP) and documented as such for future audits.

#### ✅ Phase 5.3 — Completed Tasks
- [x] Bandit & Semgrep audit performed.
- [x] Security fixes applied to rendering engines.

---

### Iteration 20 — 2026-05-17 (Gemini CLI)

### Iteration 17 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Stabilization of Docker build and fix of UI regressions (missing components, typing errors).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/Dockerfile` | Modification | Fix of `libgdk-pixbuf-2.0-0` package name for Debian Trixie. |
| `frontend/src/components/ui/card.tsx` | Creation | Added missing Card component. |
| `frontend/src/components/layout/ToolPageLayout.tsx` | Modification | Restored truncated code and stabilized interfaces. |
| `frontend/src/app/(dashboard)/tools/hibp/client.tsx` | Modification | Restored and corrected types (DataTable). |
| `frontend/src/app/(dashboard)/alerts/cve/client.tsx` | Modification | Massive correction of typing errors (TimePeriod, PageHeader, DataTable). |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Added missing `Separator` import. |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Restored full DashboardPage component (Quick stats). |
| `frontend/src/components/dashboard/APIStatusCards.tsx` | Modification | Recreation of `EmptyConnectors` and fix of `SourceStatus` type. |

#### Technical Decisions

1. **Build Integrity**: Move to Next.js production build to validate absence of TypeScript/Lint errors before delivery.
2. **UI Resilience**: Reconstruction of files truncated during previous iterations to guarantee a functional interface without placeholders.
3. **Hyphen Consistency**: Harmonization of system package names in the backend Dockerfile.

#### ✅ Phase 5 (Hardening) — Completed Tasks
- [x] Full stabilization of Full Stack Docker build.
- [x] Resolution of Next.js compilation errors.

---

### Iteration 16 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Final completion of Backend: Global reports, Profile Security, and Custom Sources.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/routers/reports.py` | Modification | Implementation of actual scan merging for global reports. |
| `backend/app/routers/settings.py` | Modification | Test endpoint for RSS/Atom sources with item preview. |
| `frontend/src/app/(dashboard)/admin/settings/client.tsx` | Modification | Full integration of CRUD and tests for custom sources. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Connection of password change and MFA enrollment actions. |
| `frontend/src/lib/api.ts` | Modification | Added `passwordChange`, `mfaSetup`, and `mfaConfirm` functions. |

#### Technical Decisions

1. **Scan Merging**: Global generation reads the physical JSON files of previous scans to ensure integrity of aggregated findings without overloading the database.
2. **Flow Validation**: Use of `feedparser` on the backend to validate an RSS feed URL before allowing it to be saved by the admin.
3. **UI Security**: Password change and MFA dialogs integrate match validations and clear state feedback.

#### ✅ Phase 1.3, 2.2 & 4.2 — Completed Tasks
- [x] Phase 1.3 — Full management of custom RSS sources.
- [x] Phase 2.2 — Profile Security 100% functional.
- [x] Phase 4.2 — Consolidated global report generation.

---

### Iteration 15 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Finalization of PDF report generation and MFA authentication flows.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/routers/reports.py` | Creation | Router for listing and exporting (PDF, HTML, JSON) reports. |
| `backend/app/report/engine.py` | Modification | WeasyPrint robustness and HTML fallback management. |
| `backend/app/engine/logic.py` | Modification | Activation of PDF generation during scans. |
| `backend/Dockerfile` | Modification | Installation of WeasyPrint system dependencies (pango, cairo, etc.). |
| `backend/app/routers/auth.py` | Modification | Finalization of `mfa/verify` and `mfa/confirm` endpoints. |
| `backend/app/engine/cve_monitor.py` | Modification | Implementation of actual OSV.dev fetcher via `modified_id.csv`. |

#### Technical Decisions

1. **PDF Isolation**: WeasyPrint is installed as an optional `[pdf]` dependency but enabled by default in the production Dockerfile to guarantee export.
2. **Report Reconstruction**: The export endpoint reads the scan JSON to reconstruct the `FinalReport` object and guarantee a PDF generation identical to the original.
3. **MFA State**: Use of Redis scan to find the `user_id` associated with a `challenge_token` in a secure and stateless manner.

#### ✅ Phase 2.2 & 4.1 — Completed Tasks
- [x] Phase 2.2 — Full MFA verification and confirmation.
- [x] Phase 4.1 — Functional and integrated PDF export.

---

### Iteration 14 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Implementation of a global Mock Data system and finalization of backend foundations.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/routers/dashboard.py` | Modification | Added dynamic mocked data generation logic. |
| `backend/app/routers/cve.py` | Modification | Demo data support if no real CVE is present. |
| `frontend/src/app/(dashboard)/admin/settings/client.tsx` | Modification | Added "Demonstration data" switch in advanced settings. |
| `frontend/src/app/(dashboard)/page.tsx" | Modification | Display of the global Mock warning banner. |
| `frontend/src/components/layout/ToolPageLayout.tsx` | Modification | Support for the "Demonstration Mode" banner on all tool pages. |
| `frontend/src/components/dashboard/APIStatusCards.tsx` | Modification | MOCK badge and Demo Mode status for connectors. |
| `frontend/src/app/(dashboard)/tools/*/page.tsx` | Modification | Detection and transmission of isMock status to clients. |
| `frontend/src/lib/api.ts` | Modification | Added `is_mock` flag to `ConnectorStatus` and `DashboardStats` interfaces. |

#### Technical Decisions

1. **On-the-fly Mock**: Mocked data is not stored in the database but generated on the fly by the API to save resources and facilitate the yes/no switch.
2. **MOCK Visibility**: Use of orange color code and explicit badges throughout the UI to ensure the user knows when they are looking at fictive data.
3. **Settings Persistence**: Mock mode is persisted in `SystemSettings` to remain active between sessions.

#### ✅ Phase 3.1 & Phase 5 (Hardening) — Completed Tasks
- [x] Phase 3.1 — Full Key-Value storage (Domain, Maintenance, Mock Mode).
- [x] Global Mock Data system (Backend + Frontend).

---

### Iteration 13 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Implementation of Backend foundations: SQLAlchemy models, Fernet encryption, and settings routers.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/models/cve.py` | Creation | SQLAlchemy models for `CVEAlert` and `CustomFeedSource`. |
| `backend/app/models/settings.py` | Creation | SQLAlchemy model for `SystemSettings` (Key-Value JSON). |
| `backend/app/core/config.py` | Modification | Added `encryption_key` to global parameters. |
| `backend/app/core/security.py` | Modification | Implementation of Fernet encryption/decryption. |
| `backend/app/routers/api_keys.py` | Modification | Securing API keys via `encrypt_secret`. |
| `backend/app/routers/settings.py` | Creation | Router for system settings and custom sources management. |
| `backend/app/routers/cve.py` | Modification | Move from mocks to actual database for alerts. |
| `backend/app/engine/cve_monitor.py` | Creation | Start of CVE collection engine implementation (NVD, CVEFeed, GitHub). |
| `backend/app/main.py` | Modification | Registration of new routers and import fixes. |

#### Technical Decisions

1. **Security-First**: Immediate implementation of Fernet encryption to avoid storing API keys in clear text from the first backend iterations.
2. **Key-Value Settings**: Use of a flexible table for system settings to avoid DB migrations at each UI configuration addition.
3. **CVE Engine**: Asynchronous structure with `CVEMonitor` natively managing NVD's strict rate-limit.

#### ✅ Phase 1.2, 2.1 & 3.1 — Completed Tasks
- [x] Phase 1.2 — DB Models for CVE & Custom Sources.
- [x] Phase 2.1 — Fernet encryption of API keys.
- [x] Phase 3.1 — SystemSettings Model.

---

### Iteration 12 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Iteration Objective**: Implementation of missing pages (CVE, Profile, Changelog) and finalization of instance parameters. Creation of the Backend roadmap.

#### ✅ Phase 6, 7 & 9 — Completed Tasks
- [x] Phase 9.1 to 9.5 — Full `/alerts/cve` page.
- [x] Phase 7.2 — User profile page (`/profile`).
- [x] Phase 6.1 — Changelog page (`/changelog`).
- [x] Phase 10.6 — "Custom sources" tab added to settings.

---

## 🤖 Next Agent — Resume Here

**Stopped at**: Backend foundations in place (Models, Security, Routers). CVE engine initialized.
**Commit**: `HEAD`
**What's left (Backend Priority)**:
- [ ] Finalize `CVEMonitor` (implement OSV.dev and actual polling).
- [ ] Connect the Profile page to actual actions (Change Password, Toggle MFA).
- [ ] Implement storage and testing of "Custom Sources" (RSS/Atom).
- [ ] Finalize actual PDF export and global report generation.

**Watch points**:
- Respect NVD rate-limits (5 req/30s).
- Use `feedparser` for custom sources (watch out for XSS injections).
- Properly migrate secrets from `.env` to DB in a secure manner.
