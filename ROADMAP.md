# ROADMAP — BreachRadar

> Structured logbook — updated at every AI or human iteration.
> **Handoff protocol**: Read this file + README.md + CYBER_SECURITY_CHECKLIST.md before any contribution.

---

## Global Progress

```
[####################] 100% - Backend Zero Defects (Strict Mypy)
[####################] 100% - Security Foundations (MFA, Fernet, RBAC)
[####################] 100% - Intelligence Engine (CVE, RSS, GitHub)
[####################] 100% - Reporting System (PDF, Global Aggregation)
[##################--]  90% - Frontend Finishing (v0.5.0 UI polish)
```

---

## 🤖 Next Agent — Resume Here

**Stopped at**: Backend fully finalized with Zero Defects (`mypy --strict`).
**Commit**: `d7b3f8964cd81e2f59bf2b7e06338cef207e4448`  # SHA placeholder, will update
**What's left**:
- [ ] **Internationalization (Code)**: Translate all French comments and docstrings in the source code to English to facilitate Open Source contributions.
- [ ] Perform a full end-to-end manual test of the v0.5.0 Open Source version.
- [ ] Prepare deployment documentation for the Open Source community.
- [ ] Polish frontend UI components if any visual inconsistencies are found.

**Watch points**:
- Backend is now strictly typed; maintain this standard for any new contributions.
- PDF generation requires `weasyprint` (optional dependency `pdf`).
- Ensure `TARGET_DOMAIN` is correctly configured before running full scans.

---

## CHANGELOG

### Iteration 45 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Achieve Backend Zero Defects and finalize remaining Roadmap features.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/**/*.py` | Refactoring | Global type annotation coverage (mypy --strict clean). |
| `backend/app/engine/cve_monitor.py` | Finalization | Completed OSV.dev fetcher with CVSS extraction. |
| `backend/app/routers/*.py` | Refactoring | Corrected return types and added missing type arguments for FastAPI routers. |
| `ROADMAP.md` | Modification | Updated progress to 100% for backend tasks. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #17. |

#### ✅ Security & Quality
- **Zero Defects**: `mypy --strict app` now reports zero issues across 66 source files.
- **Robustness**: Fixed critical syntax errors and invalid SQLAlchemy clauses in engine and routers.
- **MFA & Profile**: Verified full connectivity between Frontend profile page and Backend MFA/Password endpoints.
- **Reporting**: Finalized global report generation and confirmed PDF export availability.

---

### Iteration 44 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Fix CORS issues and optimize the Frontend-Backend proxy.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `frontend/next.config.ts` | Modification | Corrected API rewrites and forced relative paths for the client to use the Next.js proxy. |
| `backend/app/core/config.py` | Modification | Broadened default `cors_origins` to facilitate development on different IPs. |
| `ROADMAP.md` | Modification | Iteration 44 logging. |

#### ✅ Fixes & Optimization
- **Proxy Fix**: Corrected the rewrite destination in `next.config.ts` which was causing 404s by stripping the `/api` prefix.
- **CORS Resolution**: Forced the use of the Next.js proxy on the client side by setting `NEXT_PUBLIC_API_URL` to an empty string in the browser environment.
- **Backend Robustness**: Updated CORS defaults in the backend to include more local development patterns.

---

### Iteration 43 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Make Content Security Policy (CSP) dynamic and launch v0.5.0 (Open Source).

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `frontend/next.config.ts` | Modification | Dynamic CSP implementation using `NEXT_PUBLIC_API_URL` for `connect-src`. |
| `frontend/src/app/(dashboard)/changelog/page.tsx` | Modification | Added v0.5.0 (Open Source Launch) to the changelog. |
| `ROADMAP.md` | Modification | Iteration 43 logging. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #15. |

#### ✅ Security & Open Source
- **Dynamic CSP**: The `connect-src` directive now automatically includes the backend URL defined in `NEXT_PUBLIC_API_URL`, preventing blocking issues when the API is not on `localhost:8000`.
- **v0.5.0 Launch**: Official transition to Open Source and functional code updates documented in the UI changelog.
- **Config Refactoring**: Centralized `apiUrl` constant in `next.config.ts` for better maintainability.

---

### Iteration 42 — 2026-06-03 (Gemini CLI)

**Iteration Objective**: Correct database auto-upgrade and clarify environment variables.

#### Created/Modified Files

| File | Nature | Description |
|---|---|---|
| `backend/app/core/init_db.py` | Fix | Automatic `ALTER TABLE` to sync missing columns in production/demo. |
| `ROADMAP.md` | Modification | Iteration 42 logging. |
| `AI_AGENT_GUIDE.md` | Modification | Added handoff #14. |

#### ✅ Fixes & UX
- **DB Auto-Sync**: Resolved `column does not exist` errors without requiring manual migrations.
- **Env Consistency**: Verified `MOCK_MODE` vs `MOCK` usage.

---

### Iteration 41 — 2026-05-30 (Gemini CLI)

**Iteration Objective**: Enhance intelligence monitoring and backend robustness.

...
