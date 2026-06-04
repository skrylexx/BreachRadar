# AI_AGENT_GUIDE.md — Complete Guide for AI Agents


> **Repository**: BreachRadar — [https://github.com/skrylexx/BreachRadar](https://github.com/skrylexx/BreachRadar)
>
> This file is the **single entry point** for any AI agent working on this project.
> It replaces and merges: `AGENT.md`, `IA_CHANGE.md`, and `READ_BEFORE_RUN_AUDIT.md`.
>
> **Read this entire file before doing anything.**


***


## 0. Quick Resume Prompt


Copy-paste this block to start a new session on any AI agent:


```
You are resuming the development of the BreachRadar project.
Repo link: [https://github.com/skrylexx/BreachRadar](https://github.com/skrylexx/BreachRadar)


Read the AI_AGENT_GUIDE.md file IN FULL BEFORE doing anything.
It contains: your mission, traceability protocols, handoff rules,
and maintenance instructions for audit files.


Then, read in this order:
1. TECH_STACK.md   — complete technical specifications
2. ROADMAP.md      — exact progress status and next task


Scrupulously respect the traceability protocol (section 3 of this guide):
document each change in ROADMAP.md, update TECH_STACK.md and
AUDIT_INSTRUCTIONS.md if necessary, fill in the "Next Agent" section before
reaching the limit of your context window.

When a shell command is necessary, prefer using `rtk` to
reduce verbosity and token consumption on long commands.
Avoid shell command substitutions (`$(...)`, backticks) as much as possible
and prefer explicit, simple commands broken down into several steps.
```


***


## 1. Mission


Contribute to the development, maintenance, and securing of the **BreachRadar** project — a cyber intelligence/monitoring platform (Dark Web, ransomware, data breaches) composed of an OSINT engine (CLI) and a WebUI (FastAPI + Next.js).


The objective is to set and maintain **solid, modular, secure, and perfectly documented** foundations to allow fluid collaboration between AI agents (Claude, Gemini, GPT, etc.) and humans, without information loss between sessions.


***


## 2. Reference Files


### 2.1 — Steering Files Directory Structure


```
BreachRadar/
├── AI_AGENT_GUIDE.md          ← THIS file (mission, protocols, handoff, audit)
├── TECH_STACK.md              ← complete technical specifications
├── AUDIT_INSTRUCTIONS.md      ← scope and deliverables of the security audit
├── ROADMAP.md                 ← progress status and changelog
├── SECURITY_BEST-PRACTICE.md  ← project security best practices
└── audit_reports/             ← archived audit reports (YYYY-MM-DD_<sha>_audit-report.md)
```


### 2.2 — Quick Reference Table


| File | Role | Update when? |
|---------|------|-----------------------|
| `AI_AGENT_GUIDE.md` | Mission, protocols, global rules, handoff | Workflow or convention change |
| `AUDIT_INSTRUCTIONS.md` | Scope and deliverables of the audit | New component, resolved vulnerability, new pillar |
| `TECH_STACK.md` | Complete technical specifications | Any stack or dependency evolution |
| `ROADMAP.md` | Progress, CHANGELOG, next task | **At the end of every session, without exception** |
| `audit_reports/` | Archived audit reports | After each security audit |


### 2.3 — Reading Order by Session Type


**Development / Refactoring Session:**
```
1. AI_AGENT_GUIDE.md  ← this file (mandatory, in full)
2. TECH_STACK.md      ← technical specifications
3. ROADMAP.md         ← progress status and next task
```


**Security Audit Session:**
```
1. AI_AGENT_GUIDE.md      ← this file (section 8 in particular)
2. AUDIT_INSTRUCTIONS.md  ← scope and deliverables of the audit
3. TECH_STACK.md          ← complete technical specifications
```


> Never start a task without having read at least this file + ROADMAP.md.


***


## 3. Expected Deliverables by Intervention Type


### 3.1 — Development (Feature / Fix)

1. **Code**: functional, clean, and commented source files according to ROADMAP.md priorities
2. **TODO.md / ROADMAP.md** updated:
   - **Remove** completed tasks from the "What's left" or "Next Agent" section once they are fully implemented and verified.
   - Do not just check them off (`- [x]`); delete the line to keep the list focused on pending work.
3. **ROADMAP.md** updated:
   - CHANGELOG section: each modification listed precisely (file, line, nature of change)
   - Progress indicator updated (e.g., `[████░░] 60%`)
   - "Next Agent" section updated with only the remaining tasks if the session stops.
4. **README.md** updated if the architecture or installation instructions evolve


### 3.2 — Security Audit


1. **Audit report** archived in `audit_reports/YYYY-MM-DD_<short-sha>_audit-report.md`
2. **AUDIT_INSTRUCTIONS.md** updated if necessary (see section 8 below)
3. **TECH_STACK.md** updated if necessary (see section 8 below)
4. **ROADMAP.md**: add critical/high findings in the "Points of vigilance" section


### 3.3 — Refactoring / Infrastructure


1. **Refactored code** with comments explaining choices
2. **ROADMAP.md** updated with detailed CHANGELOG
3. **TECH_STACK.md** updated if the stack or architecture changes
4. **README.md** updated if the directory structure or commands change


***


## 4. Traceability Protocol (MANDATORY)


Each intervention must leave a complete and usable trace for the next agent.


### 4.1 — Before Starting


- Read ROADMAP.md to know the exact state of the project
- Identify the last audited commit in TECH_STACK.md
- Compare with the current HEAD: `git log --oneline -10`
- If critical files have changed since the last session, update TECH_STACK.md before starting
- Verify if `rtk` is available in the environment before executing verbose shell commands


### 4.2 — During the Intervention


Any change made must be documented **immediately** in ROADMAP.md according to the following format:


```markdown
### [YYYY-MM-DD] — <Short action title>
- **Modified file(s)**: `path/to/file.py` (lines X-Y)
- **Nature**: [Addition | Modification | Deletion | Refactoring | Fix | Security]
- **Reason**: Concise explanation of why
- **Impact**: Affected modules or behaviors
- **Commit**: `<SHA>` (if applicable)
```


### 4.3 — Token Management & Preventive Stop


- **Alert threshold**: at ~80% of the context window, stop writing code
- **Mandatory action before stop**: devote the last tokens to updating ROADMAP.md with:
  - What was done in the session
  - What remains to be done (with precise files and functions)
  - Points of vigilance for the next agent
  - The SHA of the last commit of the session
- **Format of the "Next Agent" section** in ROADMAP.md:


```markdown
## 🤖 Next Agent — Resume Here


**Stopped at**: `path/to/file.py` — function `function_name()`, line X
**Commit**: `<SHA>`
**What's left**:
- [ ] Task 1 (target file: `...`)
- [ ] Task 2 (target file: `...`)
**Points of vigilance**:
- Point 1
- Point 2
```


### 4.4 — Interoperability Between Agents


- Use **explicit comments** in the code: `# TODO(agent): ...`, `# NOTE: ...`, `# SECURITY: ...`
- Never leave incomplete code without a comment signaling the state: `# WIP: partial implementation — see ROADMAP.md`
- Always specify in ROADMAP.md which agent worked on which section


### 4.5 — Shell / RTK Policy


- When a shell command is necessary, **prefer `rtk`** for potentially long or verbose commands (`git status`, `git diff`, `docker ps`, `pytest`, `npm`, `pnpm`, `ls`, `find`, etc.).
- If `rtk` is available, privilege by default forms like `rtk git status`, `rtk git diff`, `rtk pytest`, `rtk docker ps`.
- Avoid shell command substitutions as much as possible:
  - `$(...)`
  - backticks
  - complex nested commands in a single call
- Prefer simple, explicit, and multi-step commands rather than a single line difficult to audit.
- If a substitution seems necessary, first look for an alternative without substitution.
- Do not assume `rtk` is available in all environments: verify its presence, then fallback on a standard command if absent.


***


## 5. Inter-Agent Handoff Protocol


### 5.1 — What the Outgoing Agent MUST Do Before Closing the Session


- [ ] Update **ROADMAP.md**: Session CHANGELOG + `Next Agent — Resume Here` section
- [ ] Update **TECH_STACK.md** if the stack has evolved (new dependencies, services, secrets)
- [ ] Update **AUDIT_INSTRUCTIONS.md** if new components have been added
- [ ] Add an entry in the **6. Handoff History** section below
- [ ] Push a commit with the message: `docs: update ROADMAP + AI_AGENT_GUIDE [end session <agent>]`


### 5.2 — What the Incoming Agent MUST Do Before Starting


- [ ] Read this entire file
- [ ] Read reference files in the order indicated in section 2.3
- [ ] Verify the last audited commit in TECH_STACK.md vs current HEAD
- [ ] Consult the `Next Agent — Resume Here` section in ROADMAP.md
- [ ] Do not modify code before having read these files


### 5.3 — Handoff Entry Format


```
### Handoff #N — YYYY-MM-DD
- **Outgoing Agent**           : [Claude / Gemini / GPT-4 / other]
- **Incoming Agent**           : [Claude / Gemini / GPT-4 / other — or "undefined"]
- **End-of-session commit**    : <SHA>
- **Tasks accomplished**       :
  - Brief summary of actions performed
- **Next task**                : Precise description + target file
- **Points of vigilance**     :
  - Point 1
  - Point 2
- **Updated files**            : ROADMAP.md | TECH_STACK.md | AUDIT_INSTRUCTIONS.md
```


***


## 6. Handoff History

### Handoff #18 — 2026-06-04

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : (Pending)
- **Tasks accomplished**:
  - **UI Polish (v0.5.0.1)**: Updated the sidebar and site changelog to reflect a new sub-version `v0.5.0.1`.
  - **Banner Internationalization**: Fully translated the domain monitoring banner (`DomainBanner.tsx`) in both English and French, removing hardcoded strings.
  - **Privacy Hardening**: Removed hardcoded placeholder email in the header user menu, now using a clean state until data is fetched.
  - **Roadmap Cleanup**: Pruned completed tasks from `ROADMAP.md` and added Iteration 46 details.
  - **Instruction Update**: Modified the guide to require AI agents to **remove** completed tasks from the roadmap instead of just checking them off, to maintain a clean workspace.
- **Next task**: Resume Backend QA (Mypy zero-defects) or finalize OSV.dev fetcher as per the roadmap.
- **Points of vigilance**:
  - The `DomainBanner` now requires translation keys in `messages/*.json`.
  - Version `v0.5.0.1` is now the reference in both the Sidebar and the Changelog page.
- **Updated files**: frontend/src/components/layout/Sidebar.tsx · frontend/src/app/(dashboard)/changelog/page.tsx · frontend/src/components/layout/DomainBanner.tsx · frontend/src/components/layout/Header.tsx · frontend/messages/*.json · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #17 — 2026-06-04

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : (Pending)
- **Tasks accomplished**:
  - **CORS Login Bug Fix**: Replaced `||` with `??` when handling `NEXT_PUBLIC_API_URL` on the client side (`login/page.tsx` and `Header.tsx`). This respects the empty string injected by `next.config.ts` and successfully uses the Next.js API proxy instead of fetching `http://localhost:8000` directly, resolving the CORS preflight errors during authentication.
- **Next task**: Continue backend QA, specifically zeroing out `mypy` errors, or verifying the fix on the user's environment.
- **Points of vigilance**:
  - Remember that `NEXT_PUBLIC_API_URL` is intentionally forced to `""` on the client. Always use `??` instead of `||` when defining default values for API URLs on the frontend.
- **Updated files**: frontend/src/app/(auth)/login/page.tsx · frontend/src/components/layout/Header.tsx · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #16 — 2026-06-03

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `6634dcf1f76bb3f45d691745849c0b09ca70d8aa`
- **Tasks accomplished**:
  - **CORS & Proxy Fix**: Resolved the "Access-Control-Allow-Origin" error by forcing the frontend to use the Next.js rewrite proxy.
  - **next.config.ts**: Updated to use an absolute `backendUrl` for the server-side proxy and CSP, while exposing an empty `NEXT_PUBLIC_API_URL` to the client to ensure relative paths are used.
  - **Backend CORS**: Broadened `cors_origins` in `backend/app/core/config.py` to support more development scenarios.
- **Next task**: Verify the fix on the user's environment and resume backend development.
- **Points of vigilance**:
  - The proxy now expects `/api` in the frontend path and correctly forwards it to the backend's `/api` prefix.
- **Updated files**: frontend/next.config.ts · backend/app/core/config.py · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #15 — 2026-06-03

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `45c6ce6f29a6f7ea046a86c7ed0210e50d377f65`
- **Tasks accomplished**:
  - **Dynamic CSP**: Refactored `frontend/next.config.ts` to make the `Content-Security-Policy` header dynamic. It now uses `NEXT_PUBLIC_API_URL` (with a fallback to `localhost:8000`) for the `connect-src` directive.
  - **v0.5.0 Open Source**: Updated `frontend/src/app/(dashboard)/changelog/page.tsx` to announce the v0.5.0 Open Source launch and functional updates.
  - **Code Quality**: Centralized `apiUrl` logic in `next.config.ts` to ensure consistency across `env`, `rewrites`, and `headers`.
- **Next task**: Resume backend development (CVE polling, profile actions) or resolve remaining `mypy` errors as indicated in ROADMAP.
- **Points of vigilance**:
  - The CSP still allows `unsafe-inline` and `unsafe-eval` for Next.js hydration, which is a known point of vigilance.
- **Updated files**: frontend/next.config.ts · frontend/src/app/(dashboard)/changelog/page.tsx · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #14 — 2026-06-03

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **Database Schema Auto-Sync**: Fixed `ProgrammingError: column users.token_version does not exist` by implementing an automatic schema upgrade in `backend/app/core/init_db.py`. Missing columns are now added via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
  - **Environment Clarification**: Clarified that the correct environment variable for demonstration mode is `MOCK_MODE` (and not `MOCK`).
- **Next task**: Resume backend development (CVE polling, profile actions) or resolve remaining `mypy` errors as indicated in ROADMAP.
- **Points of vigilance**:
  - Manual `ALTER TABLE` is used because SQLAlchemy `create_all` does not update existing tables. This is a pragmatic fix for dev/demo environments with persistent volumes.
- **Updated files**: backend/app/core/init_db.py · ROADMAP.md · AI_AGENT_GUIDE.md

***


### Handoff #1 — 2026-05-04


- **Outgoing Agent**           : Claude (Perplexity — initial structuring session)
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `08508ac`
- **Tasks accomplished**:
  - Full architecture in place (FastAPI backend + Next.js frontend + Docker Compose)
  - Creation and structuring of all steering files:
    `AGENT.md`, `READ_BEFORE_RUN_AUDIT.md`, `AUDIT_INSTRUCTIONS.md`, `TECH_STACK.md`, `IA_CHANGE.md`
- **Next task**: See `Next Agent — Resume Here` section in ROADMAP.md
- **Points of vigilance**:
  - `/auth/mfa/verify` returns `501 NOT_IMPLEMENTED` — MFA not functional as is
  - `curl | sh` in `backend/Dockerfile` — supply chain risk (no integrity check)
  - Docker images `dperson/torproxy:latest` and `travishunting/ransomlook:latest` not pinned
  - CSP with `unsafe-eval` + `unsafe-inline` in `frontend/next.config.ts`
  - `UI_REDIS_PASSWORD` visible in `redis-server` command (docker inspect / ps aux)
- **Updated files**: AGENT.md · TECH_STACK.md · AUDIT_INSTRUCTIONS.md · READ_BEFORE_RUN_AUDIT.md · IA_CHANGE.md


### Handoff #2 — 2026-05-05


- **Outgoing Agent**           : Claude (Perplexity — documentation refactoring session + UI)
- **Incoming Agent**           : Gemini (Backend construction session)
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - Merge of `AGENT.md`, `IA_CHANGE.md`, `READ_BEFORE_RUN_AUDIT.md` → `AI_AGENT_GUIDE.md`
  - Logo fix in `Sidebar.tsx` (replaced Shield icon with `images/logo_nobg.png`)
  - Added `DomainBanner.tsx` component displaying the target domain (`NEXT_PUBLIC_TARGET_DOMAIN`)
  - Integrated banner in `frontend/src/app/(dashboard)/layout.tsx`
- **Next task**: See `Next Agent — Resume Here` section in ROADMAP.md
- **Points of vigilance**: Same security points of vigilance as handoff #1 (not resolved)
- **Updated files**: AI_AGENT_GUIDE.md (new) · Sidebar.tsx · layout.tsx (dashboard) · DomainBanner.tsx (new)


***


### Handoff #3 — 2026-05-15


- **Outgoing Agent**           : Gemini (Backend construction session)
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - Backend architecture laid: SQLAlchemy models (CVE, Settings, API Keys).
  - Security: Fernet encryption implementation for secrets in DB.
  - CVE Engine: NVD API 2.0 fetchers, GitHub, CVEFeed, and rate-limit management.
  - Mock Data System: Dynamic demo data generation if keys are missing.
  - UI: Global MOCK switch, warning banners, and badges throughout the dashboard.
- **Next task**: Real polling implementation and OSV.dev fetcher finalization.
- **Points of vigilance**:
  - NVD key recommended to avoid strict rate-limit (5 req/30s).
  - MFA and Password buttons in Profile are visual but not yet linked to the backend.
- **Updated files**: TODO.md · ROADMAP.md · README.md · QUICKSTART.md · All backend/app/...


### Handoff #4 — 2026-05-18


- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - Full technical documentation generation for sub-directories.
  - Created `backend/README.md` (FastAPI, Endpoints, Local Setup).
  - Created `frontend/README.md` (Next.js, Tech stack, Local Setup).
  - Major update of `QUICKSTART.md` to include local development guide (without Docker).
  - Updated `ROADMAP.md` (Phase 5 Hardening marked 100% complete).
- **Next task**: See `Next Agent — Resume Here` section in ROADMAP.md (Focus on real CVE polling and profile actions).
- **Points of vigilance**:
  - Local guide assumes PostgreSQL and Redis are accessible natively or via isolated containers.
  - Verify `.env` consistency during Docker <-> Local switch.
- **Updated files**: backend/README.md · frontend/README.md · QUICKSTART.md · ROADMAP.md · AI_AGENT_GUIDE.md


### Handoff #5 — 2026-05-18

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - Created `ARCHITECTURE.md` file detailing the repo structure, configs, and AI files.
  - Updated `ROADMAP.md` (Iteration 23).
- **Next task**: Resume backend development (CVE polling, profile actions) as indicated in ROADMAP.
- **Points of vigilance**: No new technical points of vigilance introduced by this documentation iteration.
- **Updated files**: ARCHITECTURE.md · ROADMAP.md · AI_AGENT_GUIDE.md


### Handoff #13 — 2026-06-01

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **Docker Stack Fix**: Fixed erroneous SHA256 digests in `docker-compose.yml` for Postgres, Redis, TorProxy, and RansomLook.
  - **CSP & Black Screen Fix**: Resolved the black screen on the frontend by relaxing the CSP policy (`unsafe-inline`, `unsafe-eval`) in `next.config.ts` and removed `interest-cohort`.
  - **Database Race Condition Fix**: Implemented a distributed Redis lock in `initialize_database` to avoid `IntegrityError` (UniqueViolation) on Enums during simultaneous startup of multiple backend workers.
  - **Orchestration**: Successfully restarted the full stack (7 services).
  - **Health Validation**: Verified health of all containers (all are `healthy`).
- **Next task**: Resume backend development (CVE polling, profile actions) or resolve remaining `mypy` errors from iteration #12.
- **Points of vigilance**:
  - SHA256 digests were synchronized with functional local versions.
  - CSP was eased to allow normal Next.js operation in production without complex nonces.
- **Updated files**: docker-compose.yml · frontend/next.config.ts · backend/app/main.py · backend/app/core/init_db.py · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #12 — 2026-06-01

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **Gemini CI/CD Skill**: Created the `cicd-expert` skill to automate and guide pipeline maintenance.
  - **Quality Pipeline++**: Added `mypy` (static typing) and `bandit` (security linting) in GitHub Actions.
  - **Bug Fixes (CI-driven)**: Corrected several typing and logic errors identified by new tools (Scheduler, ScanSchema, etc.).
- **Next task**: Resolve 28 remaining `mypy` errors (see local output) or continue development of backend features (CVE polling, profile actions).
- **Points of vigilance**:
  - `mypy` configuration in `pyproject.toml` was relaxed (`strict = false`) to allow a gradual introduction without blocking all development.
  - `bandit` now specifically ignores a false positive in `app/schemas/scan.py` via `# nosec`.
- **Updated files**: .github/workflows/ci.yml · backend/pyproject.toml · ROADMAP.md · AI_AGENT_GUIDE.md · Several backend files for corrections.

***

### Handoff #11 — 2026-06-01

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **CI/CD GitHub Actions**: Created the `.github/workflows/ci.yml` workflow.
  - **Quality Pipeline**: Automated linting (Ruff, ESLint), Next.js build, and pytest tests.
  - **Automated Security Audit**: Integrated `detect-secrets`, `npm audit`, and `pip-audit` into the pipeline.
  - **Infrastructure Verification**: Added Docker images build validation in CI.
- **Next task**: Configure "Branch Protection Rules" on GitHub to make these checks mandatory before any merge to `main`.
- **Points of vigilance**:
  - `pip-audit` may fail if critical vulnerabilities are found in Python dependencies (expected behavior to block insecure PRs).
  - Next.js build in CI requires environment variables (Mocks used in workflow).
- **Updated files**: .github/workflows/ci.yml · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #10 — 2026-06-01

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **Internationalization (i18n)**: Full FR/EN support setup on the frontend via `next-intl`.
  - **Translation**: Coverage of critical pages (Dashboard, Login, MFA, Profile, Intelligence/Monitoring, Scans, Reports).
  - **Localization**: Dynamic date formats and durations management according to user language.
  - **Documentation**: Updated `ROADMAP.md` (Iteration 36).
- **Next task**: Continue translation of specific tool pages (HIBP, GitHub, etc.) and remaining UI components (confirmation modals, complex tooltips).
- **Points of vigilance**:
  - Properly use `useTranslations` hook in client components and `getTranslations` in server components.
  - Ensure new translation keys are added to both `en.json` and `fr.json` files simultaneously.
- **Updated files**: frontend/messages/*.json · frontend/src/app/(dashboard)/**/*.tsx · ROADMAP.md · AI_AGENT_GUIDE.md

***

### Handoff #9 — 2026-06-01

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : *(see commit associated with this push)*
- **Tasks accomplished**:
  - **Project Immersion**: Deep analysis of documentation, architecture, and security standards.
  - **Security Roadmap**: Created a full test strategy in `TODO.md` (Audit, Code Audit/Pentest, RBAC, Front-Back Communications).
  - **Skill Activation**: Initialized the `senior-webapp-cyber-auditor` skill to guide the next securing steps.
- **Next task**: Start Phase 1 audit (Supply Chain, Docker tags, Secrets leaks) as defined in `TODO.md` and follow the `CYBER_SECURITY_CHECKLIST.md`.
- **Points of vigilance**:
  - Critical vulnerabilities in Next.js 15.1.3 must be addressed first during Phase 1 testing.
  - Ensure Docker images are pinned via SHA256 to avoid tag poisoning attacks.
- **Updated files**: TODO.md · ROADMAP.md · AI_AGENT_GUIDE.md · CYBER_SECURITY_CHECKLIST.md


### Handoff #8 — 2026-05-23

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `cb12e58` (base) + Audit Reports
- **Tasks accomplished**:
  - **Versions Security Audit**:
    - Backend SCA Scan (`pip-audit`): 6 vulnerabilities found (`idna` < 3.15, `urllib3` < 2.7.0).
    - Frontend SCA Scan (`npm audit`): 6 vulnerabilities found, including **Next.js 15.1.3 (CRITICAL)**.
    - Created `PROCEDURE_CHECKS.md` to systematize future checks.
    - Updated `TECH_STACK.md` with real system versions (Python 3.14.3, Node 22.12.0).
- **Next task**: Remediate critical vulnerabilities (Update Next.js, urllib3, idna).
- **Points of vigilance**:
  - **URGENT**: The used Next.js version has documented RCE and SSRF risks.
  - The local Python version (3.14) is well ahead of the Docker image (3.12).
- **Updated files**: ROADMAP.md · AI_AGENT_GUIDE.md · TODO.md · PROCEDURE_CHECKS.md · TECH_STACK.md

***

### Handoff #7 — 2026-05-23

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `77a21a7` (base) + v0.2.3
- **Tasks accomplished**:
  - **MFA & Session Refactoring**: Fixed premature logout, added backup codes, recovery mode, UX auto-focus.
  - **Digital Intelligence/Monitoring (v0.2.3)**:
    - Implemented `IntelligenceMonitor` engine (RSS, GitHub, Pastebin stub).
    - `CRITICAL` alerting system via Webhook/Email integrated into the collector.
    - `/intelligence` interface with dynamic filters (Severity, Read/Unread).
    - Added 5 major cyber sources including IT-Connect.
  - Diagnostic and correction of backend crash related to DB schema (SQL migration performed).
  - Validation of the entire Docker stack (all services are healthy).
- **Next task**: Advanced NotificationEngine linkage (Templating) and mass actions on the Feed.
- **Points of vigilance**:
  - `cyber_findings.extra_metadata` is a flexible JSONB, ideal for storing specificities of each source.
  - Deduplication is based on a SHA256 hash of the URL/external_id.
- **Updated files**: ROADMAP.md · AI_AGENT_GUIDE.md · README.md · TODO.md · changelog/page.tsx

***

### Handoff #6 — 2026-05-21

- **Outgoing Agent**           : Gemini CLI
- **Incoming Agent**           : undefined
- **End-of-session commit**    : `92c060f`
- **Tasks accomplished**:
  - Full analysis of current MFA implementation (Backend auth.py & Frontend login page).
  - Created a detailed implementation roadmap in `TODO.md` (MFA flow, Admin controls, Hardening).
- **Next task**: Implement `/mfa` page in the frontend and update middleware to authorize its access (see `TODO.md`).
- **Points of vigilance**:
  - Next.js middleware redirects to `/login` if `access_token` is missing, which blocks `/mfa`.
  - Backend `MFAVerifyRequest` schema does not contain a user identifier (requires email or Redis scan of the challenge token).
- **Updated files**: TODO.md · ROADMAP.md · AI_AGENT_GUIDE.md


***


## 7. Style & Quality Instructions


- **Maximum technical precision** — zero generality, zero approximation
- **Clean, commented, and modular code** — each function has a docstring, each module has a header comment
- **No useless chatter** — focus on execution and progress tracking
- **Mandatory tests** for all new business code: pytest + pytest-asyncio
- **Linting before commit**: `ruff check .` and `mypy` must not return any blocking errors
- **Secrets**: never hardcode a sensitive value — always use `settings` (pydantic-settings)
- **No `print()`** in production — use the logger configured in `main.py`
- **Favor `rtk`** to reduce useless shell command output when the tool is available
- **Avoid shell substitutions** when an explicit alternative exists


***


## 8. Audit File Maintenance (Before Any Audit Run)


> This section replaces `READ_BEFORE_RUN_AUDIT.md`. To be read before any security audit session.


### 8.1 — Pre-run Verification


Before launching the audit, perform the following verifications.


**Compare current commit with last audited commit:**


Retrieve the SHA of the last audited commit in `TECH_STACK.md` (`Dernier commit audité` field).
Compare with the current HEAD of the repository via:


```bash
git log --oneline -20
git diff <sha_last_audit> HEAD --name-only
```


If critical files have changed since the last audit, proceed to the next step.
If no change, the audit can start directly.


**Classify modified files by impact:**


| Modified File | Required Action |
|-----------------|----------------|
| `backend/app/routers/*.py` | Update section 1.2 of `AUDIT_INSTRUCTIONS.md` + section 2 of `TECH_STACK.md` |
| `backend/app/core/config.py` | Update Secrets and Backend sections of `TECH_STACK.md` |
| `backend/app/core/security.py` | Update section 1.1 of `AUDIT_INSTRUCTIONS.md` |
| `backend/pyproject.toml` | Update dependencies in `TECH_STACK.md` section 2 |
| `frontend/package.json` | Update dependencies in `TECH_STACK.md` section 3 |
| `frontend/next.config.ts` | Update section 3 of `TECH_STACK.md` (CSP headers) |
| `docker-compose.yml` | Update section 4 of `TECH_STACK.md` |
| `backend/Dockerfile` or `frontend/Dockerfile` | Update section 4 of `TECH_STACK.md` |
| `backend/app/engine/logic.py` | Update section 1.6 of `AUDIT_INSTRUCTIONS.md` |
| `backend/app/clients/` | Update section 6 of `TECH_STACK.md` (OSINT sources) |
| `.env.example` | Update section 5 of `TECH_STACK.md` (secrets) |


### 8.2 — When to update TECH_STACK.md


Update `TECH_STACK.md` **obligatorily** if any of the following conditions are met:


| Condition | Section to update |
|-----------|--------------------------|
| New dependency in `pyproject.toml` or `package.json` | Section 2 (Backend) or 3 (Frontend) |
| Version change of an existing dependency | Corresponding section + check CVE |
| New service in `docker-compose.yml` | Section 4 (Containerization) |
| New variable in `.env.example` | Section 5 (Secrets) |
| New OSINT source in `sources.yaml` or `clients/` | Section 6 (OSINT Sources) |
| New router or module in `backend/app/` | Section 2 (Backend) + Section 8 (Key files) |
| Change of base Docker image | Section 4 (Containerization) |


After update, refresh the field:
```
Dernier commit audité : <SHA>
Date de mise à jour   : YYYY-MM-DD
```


### 8.3 — When to update AUDIT_INSTRUCTIONS.md


Update `AUDIT_INSTRUCTIONS.md` **obligatorily** if any of the following conditions are met:


| Condition | Action |
|-----------|--------|
| New file in `backend/app/routers/` | Add in target files of the concerned pillar |
| New critical functionality (SSO, export, import, new role) | Add analysis points in the relevant pillar |
| Resolved documented vulnerability | Mark `[RESOLVED - commit <SHA>]` then archive |
| Infrastructure change (Nginx, Kubernetes, reverse proxy...) | Update pillar 1.4 |
| New authentication endpoint | Update pillar 1.1 |


**Golden Rule**: never delete an analysis point without having marked it `[RESOLVED]` with the correction commit SHA.


### 8.4 — Archiving Audit Reports


Each audit report produced must be saved according to the following convention:


```
audit_reports/
└── YYYY-MM-DD_<short-sha>_audit-report.md
```


Example: `audit_reports/2026-05-04_a3f9c12_audit-report.md`


The report must include in the header:


```
Commit audited  : <Full SHA>
Audit date     : YYYY-MM-DD
Auditor        : [Name / AI Tool]
Files read     : TECH_STACK.md, AUDIT_INSTRUCTIONS.md (current versions)
```


### 8.5 — Final Consistency Check (end of audit session)


- [ ] `TECH_STACK.md` reflects the current state of the repository (no missing dependency, no undocumented service)
- [ ] `AUDIT_INSTRUCTIONS.md` covers all active files and components of the repository
- [ ] The field `Dernier commit audité` in `TECH_STACK.md` is up to date
- [ ] The audit report is archived in `audit_reports/` with the naming convention
- [ ] Fixed vulnerabilities since the last audit have been removed or marked `[RESOLVED]` in `AUDIT_INSTRUCTIONS.md`
- [ ] No sensitive information (API key, password, token) appears in clear text in the documentation files
