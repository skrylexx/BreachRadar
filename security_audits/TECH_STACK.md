=============================================================================
CONTEXTE TECHNIQUE — AUDIT DE SÉCURITÉ — BreachRadar
Dépôt : https://github.com/skrylexx/BreachRadar
=============================================================================

────────────────────────────────────────────
1. ARCHITECTURE GÉNÉRALE
────────────────────────────────────────────
BreachRadar est une plateforme de veille cyber (Dark Web, ransomware, fuites de
données) composée d'une couche principale WebUI (FastAPI + Next.js) qui
orchestrent le moteur BreachRadar.

L'ensemble est orchestré via Docker Compose avec des réseaux isolés :
  - ransomlook_net  → réseau interne pour RansomLook + Tor + Redis
  - ui_net          → réseau interne pour la stack WebUI (FastAPI + PostgreSQL + Redis + Next.js)

Services Docker :
  - ransomlook-redis    : redis:7-alpine           (réseau ransomlook_net)
  - ransomlook-tor      : dperson/torproxy:latest  (réseau ransomlook_net)
  - ransomlook-app      : travishunting/ransomlook:latest — port 127.0.0.1:${RANSOMLOOK_PORT:-8888} uniquement
  - breachradar-postgres: postgres:16-alpine       (réseau ui_net)
  - breachradar-ui-redis: redis:7-alpine + auth    (réseau ui_net)
  - breachradar-api     : build local backend/     — port 127.0.0.1:${API_PORT:-8000} uniquement
  - breachradar-ui      : build local frontend/    — port 127.0.0.1:${UI_PORT:-3000} uniquement

Tous les ports sont liés à 127.0.0.1 (jamais 0.0.0.0) par défaut. Les ports et
hosts peuvent être surchargés via la section NETWORK de .env.example
(UI_HOST/UI_PORT/API_HOST/API_PORT/RANSOMLOOK_HOST/RANSOMLOOK_PORT).

────────────────────────────────────────────
2. BACKEND — FastAPI
────────────────────────────────────────────
Runtime     : Python 3.14.3 (Local) / 3.12 (Docker)
Framework   : FastAPI >= 0.115.5
Serveur     : Uvicorn 0.32.1 avec 2 workers (pas de --reload en prod)
Gestion deps: uv (astral.sh) + pyproject.toml (hatchling)

Image Docker base : python:3.12-slim
  - uv installé via curl | sh depuis astral.sh (vecteur d'attaque supply chain)
  - Utilisateur non-root : brapi:brapi
  - WORKDIR : /app
  - Port exposé : 8000

Dépendances principales (Audit 2026-05-23) :
  - SQLAlchemy 2.0 (asyncio) + asyncpg 0.30 → PostgreSQL async
  - Alembic 1.14                             → migrations (NON lancé auto au démarrage)
  - redis[hiredis] 5.2 + slowapi 0.1.9      → rate limiting (200 req/min par IP)
  - python-jose[cryptography] 3.3.0          → JWT (HS256)
  - passlib[bcrypt] 1.7.4 + bcrypt 4.0.1     → hash mots de passe (bcrypt, limite 72 octets)
  - pyotp 2.9.0 + qrcode[pil] 8.0           → TOTP/MFA (RFC 6238, fenêtre ±1)
  - pydantic 2.10.3 + pydantic-settings 2.6  → validation des entrées
  - email-validator 2.2.0
  - httpx 0.27.2 + aiohttp 3.9              → appels HTTP sortants
  - apscheduler 3.10 + croniter 2.0         → scheduler de scans
  - aiosmtplib 3.0.2 + jinja2 3.1.5        → notifications email
  - cryptography 42                          → chiffrement
  - feedparser 6.0                           → parsing de flux RSS/Atom
  - weasyprint 62 (optionnel)               → export PDF
  - telethon 1.36 (optionnel)               → scraping Telegram

Linter : ruff (sélection E,W,F,I,N,UP,S,B,A,C4,RET,SIM) — ignore S101, S603
Typage  : mypy strict

────────────────────────────────────────────
3. FRONTEND — Next.js
────────────────────────────────────────────
Framework   : Next.js 15.1.3 (VULNÉRABLE - CRITIQUE)
Runtime     : Node.js 22.12.0 (Local) / Node.js 20 (Docker)
Langage     : TypeScript 5
Styling     : Tailwind CSS 3.4.17 + postcss
Composants  : Shadcn/ui (Radix UI primitives)
Charts      : Recharts 2.14.1
Forms       : react-hook-form 7.54.2 + @hookform/resolvers + zod 3.24.1
i18n        : next-intl 3.26.3
Notifications: sonner 1.7.1
Auth client : js-cookie 3.0.5 (VULNÉRABLE - HIGH)
Icons       : lucide-react 0.469.0

────────────────────────────────────────────
4. CONTENEURISATION — POINTS NOTABLES
────────────────────────────────────────────
Docker Engine   : 29.4.3
Docker Compose  : v5.1.3

────────────────────────────────────────────
5. GESTION DES SECRETS
────────────────────────────────────────────
Méthode    : fichier .env non versionné (présent dans .gitignore)
Secrets gérés : UI_DB_PASSWORD, UI_REDIS_PASSWORD, UI_JWT_SECRET, etc.

=============================================================================
MÉTADONNÉES D'AUDIT
─────────────────────────────────────────────
Dernier commit audité : cb12e58
Date de mise à jour   : 2026-05-23
=============================================================================
