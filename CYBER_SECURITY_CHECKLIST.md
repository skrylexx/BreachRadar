# 🛡️ Cyber Verification & Maintenance Procedure — BreachRadar

This document details the critical control points to validate at each development iteration to maintain a maximum security level ("Secure by Default").

## 📅 Recommended Frequency: At every Pull Request or major iteration.

---

## 🏗️ 1. Supply Chain Integrity (Docker & Build)
*Goal: Prevent build chain poisoning and guarantee reproducibility.*

- [ ] **Image Pinning**: Verify that all `FROM` in `Dockerfile` and `image:` in `docker-compose.yml` use SHA256 hashes (`image:tag@sha256:...`).
- [ ] **Package Installation**: Prohibit the use of `curl | sh`. Use official images (e.g., `COPY --from=ghcr.io/astral-sh/uv...`) or package managers with signatures.
- [ ] **Container Privileges**: 
    - [ ] `security_opt: [no-new-privileges:true]` enabled on all services.
    - [ ] `cap_drop: [ALL]` by default, with surgical reactivation only if necessary (`SETUID`, `SETGID`, etc.).
    - [ ] Non-root user (`brapi`, `nextjs`) used at runtime.

## 🔍 2. Application Security & Anti-Injection
*Goal: Neutralize classic web attack vectors (OWASP Top 10).*

- [ ] **SSRF Validation**: Any user parameter serving as a scan target (e.g., `target_domain`) must be validated by a strict Regex and a blacklist of local IPs (127.0.0.1, localhost).
- [ ] **OSINT Sanitization**: Verify that raw data from third-party APIs passes through `DataSanitizer` before storage and that the frontend uses auto-escaping (default in React/Next.js).
- [ ] **SQL/Command Injections**: 
    - [ ] Exclusively use SQLAlchemy ORM with bound parameters (no f-strings in queries).
    - [ ] Prohibit `shell=True` in `subprocess` and validate arguments passed to `theHarvester`.
- [ ] **Webhooks**: Systematically verify HMAC signatures (e.g., `X-Hub-Signature-256` for GitHub).

## 🔐 3. Authentication & Access Control (RBAC)
*Goal: Ensure privilege isolation and account protection.*

- [x] **MFA (Multi-Factor Auth)**: 
    - [x] Verify that the TOTP secret is encrypted in the database via Fernet.
    - [x] Validate the presence of brute-force protection (Redis counter) on the `/mfa/verify` endpoint.
    - [x] Ensure that backup codes are hashed (Bcrypt).
- [x] **API Permissions**: Verify that sensitive endpoints (`/settings`, `/api_keys`, `/users`) use the `AdminUser` dependency and not `ViewerUser`.
- [x] **Secrets Management**: 
    - [x] No API keys or passwords should appear in logs (`logger.info`).
    - [x] OSINT API keys must never be returned to the frontend (masking or omission in Pydantic schemas).

## 🌐 4. Communication & Session Security
*Goal: Protect data in transit and access tokens.*

- [x] **Cookie Security**: 
    - [x] `HttpOnly: true`, `Secure: true` (in prod), `SameSite: Lax`.
    - [x] `path` restricted for the `refresh_token` (e.g., `/api/v1/auth/refresh`).
- [x] **HTTP Headers (CSP)**: 
    - [x] `Content-Security-Policy` without `unsafe-inline` or `unsafe-eval` for scripts.
    - [x] `HSTS` enabled with a long `max-age` (1 year).
    - [x] `Permissions-Policy` configured to disable camera/microphone.
- [x] **CORS**: `allow_origins` restricted to authorized domains (never `*`).

## 📦 5. Dependency Monitoring & SCA (Software Composition Analysis)
*Goal: Identify and fix vulnerabilities in third-party libraries.*

- [x] **Backend Scan**: Run `rtk python -m pip_audit` (or equivalent) in the `backend/` directory.
- [x] **Frontend Scan**: Run `npm audit` in the `frontend/` directory.
- [x] **Critical Vigilance**: Monitor versions of `Next.js`, `FastAPI`, `Cryptography`, and `Pydantic`.

---

## 🛠️ Quick Verification Tools
```bash
# Check for unhashed Docker images
grep "image:" docker-compose.yml | grep -v "@sha256"

# Search for dangerous subprocess usage
grep -r "shell=True" backend/app/

# Check for potentially unprotected Admin endpoints
grep -r "ViewerUser" backend/app/routers/ | grep -E "settings|api_keys|users"
```
