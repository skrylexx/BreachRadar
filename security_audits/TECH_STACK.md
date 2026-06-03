=============================================================================
TECHNICAL CONTEXT — SECURITY AUDIT — BreachRadar
Repository: https://github.com/skrylexx/BreachRadar
=============================================================================

────────────────────────────────────────────
1. GENERAL ARCHITECTURE
────────────────────────────────────────────
BreachRadar is a cyber intelligence platform (Dark Web, ransomware, data leaks)
composed of a main WebUI layer (FastAPI + Next.js) that orchestrates the
BreachRadar engine.

The whole system is orchestrated via Docker Compose with isolated networks:
  - ransomlook_net  → internal network for RansomLook + Tor + Redis
  - ui_net          → internal network for the WebUI stack (FastAPI + PostgreSQL + Redis + Next.js)

Docker Services:
  - ransomlook-redis    : redis:7-alpine           (ransomlook_net network)
  - ransomlook-tor      : dperson/torproxy:latest  (ransomlook_net network)
  - ransomlook-app      : travishunting/ransomlook:latest — port 127.0.0.1:${RANSOMLOOK_PORT:-8888} only
  - breachradar-postgres: postgres:16-alpine       (ui_net network)
  - breachradar-ui-redis: redis:7-alpine + auth    (ui_net network)
  - breachradar-api     : local backend/ build     — port 127.0.0.1:${API_PORT:-8000} only
  - breachradar-ui      : local frontend/ build    — port 127.0.0.1:${UI_PORT:-3000} only

All ports are bound to 127.0.0.1 (never 0.0.0.0) by default. Ports and
hosts can be overridden via the NETWORK section of .env.example
(UI_HOST/UI_PORT/API_HOST/API_PORT/RANSOMLOOK_HOST/RANSOMLOOK_PORT).

────────────────────────────────────────────
2. BACKEND — FastAPI
────────────────────────────────────────────
Runtime     : Python 3.14.3 (Local) / 3.12 (Docker)
Framework   : FastAPI >= 0.115.5
Server      : Uvicorn 0.32.1 with 2 workers (no --reload in prod)
Deps Mgt    : uv (astral.sh) + pyproject.toml (hatchling)

Base Docker Image: python:3.12-slim
  - uv installed via curl | sh from astral.sh (supply chain attack vector)
  - Non-root user : brapi:brapi
  - WORKDIR : /app
  - Exposed Port : 8000

Main Dependencies (Audit 2026-05-23):
  - SQLAlchemy 2.0 (asyncio) + asyncpg 0.30 → async PostgreSQL
  - Alembic 1.14                             → migrations (NOT auto-run at startup)
  - redis[hiredis] 5.2 + slowapi 0.1.9      → rate limiting (200 req/min per IP)
  - python-jose[cryptography] 3.3.0          → JWT (HS256)
  - passlib[bcrypt] 1.7.4 + bcrypt 4.0.1     → password hashing (bcrypt, 72-byte limit)
  - pyotp 2.9.0 + qrcode[pil] 8.0           → TOTP/MFA (RFC 6238, window ±1)
  - pydantic 2.10.3 + pydantic-settings 2.6  → input validation
  - email-validator 2.2.0
  - httpx 0.27.2 + aiohttp 3.9              → outgoing HTTP calls
  - apscheduler 3.10 + croniter 2.0         → scan scheduler
  - aiosmtplib 3.0.2 + jinja2 3.1.5        → email notifications
  - cryptography 42                          → encryption
  - feedparser 6.0                           → RSS/Atom feed parsing
  - weasyprint 62 (optional)               → PDF export
  - telethon 1.36 (optional)               → Telegram scraping

Linter : ruff (select E,W,F,I,N,UP,S,B,A,C4,RET,SIM) — ignore S101, S603
Typing : mypy strict

────────────────────────────────────────────
3. FRONTEND — Next.js
────────────────────────────────────────────
Framework   : Next.js 15.1.3 (VULNERABLE - CRITICAL)
Runtime     : Node.js 22.12.0 (Local) / Node.js 20 (Docker)
Language    : TypeScript 5
Styling     : Tailwind CSS 3.4.17 + postcss
Components  : Shadcn/ui (Radix UI primitives)
Charts      : Recharts 2.14.1
Forms       : react-hook-form 7.54.2 + @hookform/resolvers + zod 3.24.1
i18n        : next-intl 3.26.3
Notifications: sonner 1.7.1
Auth client : js-cookie 3.0.5 (VULNERABLE - HIGH)
Icons       : lucide-react 0.469.0

────────────────────────────────────────────
4. CONTAINERIZATION — KEY POINTS
────────────────────────────────────────────
Docker Engine   : 29.4.3
Docker Compose  : v5.1.3

────────────────────────────────────────────
5. SECRETS MANAGEMENT
────────────────────────────────────────────
Method     : unversioned .env file (present in .gitignore)
Managed Secrets : UI_DB_PASSWORD, UI_REDIS_PASSWORD, UI_JWT_SECRET, etc.

=============================================================================
AUDIT METADATA
─────────────────────────────────────────────
Last audited commit : cb12e58
Update date         : 2026-05-23
=============================================================================
