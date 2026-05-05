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
Runtime     : Python 3.12
Framework   : FastAPI >= 0.115.5
Serveur     : Uvicorn 0.32.1 avec 2 workers (pas de --reload en prod)
Gestion deps: uv (astral.sh) + pyproject.toml (hatchling)

Image Docker base : python:3.12-slim
  - uv installé via curl | sh depuis astral.sh (vecteur d'attaque supply chain)
  - Utilisateur non-root : brapi:brapi
  - WORKDIR : /app
  - Port exposé : 8000

Dépendances principales :
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

Structure des modules :
  backend/app/
    main.py          — point d'entrée, middleware, routeurs
    core/
      config.py      — pydantic-settings (12 Ko)
      database.py    — engine SQLAlchemy async
      redis.py       — client Redis async
      security.py    — bcrypt, JWT, TOTP
      init_db.py     — création admin initial au démarrage
      source_registry.py — registre des sources OSINT
      sources.yaml   — config sources (HIBP, Shodan, etc.)
      group_names.yaml   — liste groupes ransomware
    routers/
      auth.py        — login, refresh, MFA (10 Ko)
      users.py       — CRUD utilisateurs
      scans.py       — déclenchement et suivi des scans
      api_keys.py    — gestion des clés API internes
      webhooks.py    — endpoints webhooks sortants
      health.py      — healthcheck /health
    models/          — SQLAlchemy ORM
    schemas/         — Pydantic v2 schemas
    dependencies/    — FastAPI dependencies (auth, RBAC)
    clients/         — clients HTTP vers sources OSINT
    engine/
      logic.py       — ScanManager
      scheduler.py   — ScanScheduler (APScheduler)
    notifications/   — alertes email/webhook
    report/          — génération de rapports
    resolver/        — résolution DNS/OSINT

Middlewares configurés (dans main.py) :
  - CORSMiddleware   : origines depuis settings.cors_origins (env CORS_ORIGINS)
                       allow_credentials=True, allow_headers=["*"]
  - TrustedHostMiddleware : allowed_hosts depuis settings.allowed_hosts
  - SlowAPIMiddleware : rate limiting global 200 req/min par IP

Gestion des erreurs :
  - Handler global masque les stack traces en production (env ENVIRONMENT=production)
  - docs_url et redoc_url désactivés en production

Auth & Autorisation :
  - JWT access token : 15 min (HS256), refresh token : 7 jours
  - RBAC : 2 rôles (admin / viewer) avec politique de mot de passe différenciée
  - MFA TOTP optionnel (pyotp, RFC 6238)
  - Politique de rotation des mots de passe (exemption si len >= 24)
  - admin initial créé au premier démarrage depuis variables d'env
    (INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_PASSWORD, avec fallback sur UI_ADMIN_*)
  - Validation explicite : INITIAL_ADMIN_PASSWORD >= 16 caractères et <= 72 octets

Migrations DB :
  - Alembic présent MAIS Base.metadata.create_all() est utilisé au startup
    (pas d'exécution automatique des migrations Alembic)

────────────────────────────────────────────
3. FRONTEND — Next.js
────────────────────────────────────────────
Framework   : Next.js 15.1.3 (output: standalone)
Runtime     : Node.js 20 (node:20-alpine, build multi-stage)
Langage     : TypeScript 5
Styling     : Tailwind CSS 3.4.17 + postcss
Composants  : Shadcn/ui (Radix UI primitives)
              @radix-ui/react-{avatar,dialog,dropdown-menu,label,select,
              separator,slot,switch,tabs,tooltip}
Charts      : Recharts 2.14.1
Forms       : react-hook-form 7.54.2 + @hookform/resolvers + zod 3.24.1
i18n        : next-intl 3.26.3
Notifications: sonner 1.7.1
Auth client : js-cookie 3.0.5 (gestion cookies côté client)
Icons       : lucide-react 0.469.0

Image Docker : node:20-alpine (builder + runner)
  - Build multi-stage : deps → builder → runner
  - Utilisateur non-root : nextjs (uid 1001)
  - WORKDIR : /app
  - Port exposé : 3000
  - ENV HOSTNAME="0.0.0.0" dans le runner (écoute toutes interfaces dans le conteneur)

Proxy API : next.config.ts — toutes les requêtes /api/* sont rewritées vers
            ${NEXT_PUBLIC_API_URL} (variable d'env injectée au build)

Headers de sécurité (next.config.ts) :
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Referrer-Policy: strict-origin-when-cross-origin
  - Content-Security-Policy:
      default-src 'self'
      script-src 'self' 'unsafe-inline' 'unsafe-eval'   ← POINT D'ATTENTION
      style-src 'self' 'unsafe-inline' https://fonts.googleapis.com
      font-src 'self' https://fonts.gstatic.com
      img-src 'self' data: blob:
      connect-src 'self' http://localhost:8000           ← HTTP en dur (non HTTPS)

Variables d'environnement exposées côté client :
  - NEXT_PUBLIC_API_URL (injectée au build-time dans le bundle JS, visible navigateur)

Absence constatée :
  - Pas de Strict-Transport-Security (HSTS)
  - Pas de Permissions-Policy
  - Pas de X-XSS-Protection

────────────────────────────────────────────
4. CONTENEURISATION — POINTS NOTABLES
────────────────────────────────────────────
Backend Dockerfile :
  - Base : python:3.12-slim (image Debian slim)
  - Installation de uv via : curl -LsSf https://astral.sh/uv/install.sh | sh
    → Téléchargement et exécution de script depuis internet au build
    → L'uv binaire est placé dans /root/.cargo/bin et PATH est mis à jour
    → ⚠ UV_SYSTEM_PYTHON=1 : uv installe dans Python système (pas de venv isolé)
  - Layer de copie du code source APRÈS installation des dépendances (bonne pratique)
  - Utilisateur non-root brapi créé correctement après chown

Frontend Dockerfile :
  - Base : node:20-alpine
  - npm ci utilisé (lockfile respecté)
  - Build multi-stage correct
  - NEXT_PUBLIC_API_URL passé comme ARG (valeur encodée dans le bundle JS statique)
  - NEXT_TELEMETRY_DISABLED=1 (pas de télémétrie Next.js)

Docker Compose :
  - Secrets injectés via variables d'environnement (pas de Docker Secrets natifs)
  - UI_DB_PASSWORD, UI_REDIS_PASSWORD, UI_JWT_SECRET : requis avec :?error
  - Ports liés à 127.0.0.1 par défaut (UI_HOST/UI_PORT/API_HOST/API_PORT/RANSOMLOOK_HOST/RANSOMLOOK_PORT)
  - ransomlook-tor : image dperson/torproxy:latest (tag latest, pas de digest fixé)
  - ransomlook-app : travishunting/ransomlook:latest (tag latest, pas de digest fixé)
  - Volume ./reports monté en bind mount dans breachradar-api
  - Pas de read_only: true sur les conteneurs
  - Pas de cap_drop / cap_add déclarés
  - Pas de seccomp / apparmor profiles
  - healthchecks correctement configurés sur tous les services

────────────────────────────────────────────
5. GESTION DES SECRETS
────────────────────────────────────────────
Méthode    : fichier .env non versionné (présent dans .gitignore)
             + .env.example versionné avec placeholders CHANGE_ME_*
             + validation au démarrage via pydantic-settings (:?required)

Secrets gérés :
  - UI_DB_PASSWORD     → PostgreSQL
  - UI_REDIS_PASSWORD  → Redis (passé aussi dans la commande redis-server ⚠)
  - UI_JWT_SECRET      → signature JWT HS256
  - UI_ADMIN_EMAIL / UI_ADMIN_PASSWORD → admin initial WebUI
  - INITIAL_ADMIN_EMAIL / INITIAL_ADMIN_PASSWORD → admin initial backend
  - SMTP_PASSWORD      → serveur mail
  - HIBP_API_KEY, GITHUB_TOKEN, GITLAB_TOKEN, URLSCAN_API_KEY, OTX_API_KEY
  - LEAKCHECK_API_KEY, DEHASHED_EMAIL/API_KEY, INTELX_API_KEY,
    SHODAN_API_KEY, HUNTER_API_KEY
  - TELEGRAM_API_ID / TELEGRAM_API_HASH

Risques identifiés :
  - UI_REDIS_PASSWORD visible dans la commande redis-server (docker inspect)
  - NEXT_PUBLIC_API_URL injectée dans le bundle JS public (intentionnel mais à documenter)
  - Pas de gestionnaire de secrets type Vault / AWS Secrets Manager
  - Pas de rotation automatique des secrets

────────────────────────────────────────────
6. SOURCES OSINT INTÉGRÉES (SURFACE D'ATTAQUE)
────────────────────────────────────────────
Sources externes interrogées par le moteur :
  - Have I Been Pwned (HIBP)
  - GitHub / GitLab (leak scan)
  - URLScan.io
  - AlienVault OTX
  - LeakCheck, Dehashed, IntelX, Shodan, Hunter.io
  - RansomLook (via proxy Tor interne ou API SaaS)
  - Telegram (via Telethon)
  - Flux RSS/Atom (feedparser)

────────────────────────────────────────────
7. OUTILLAGE DE SÉCURITÉ EXISTANT
────────────────────────────────────────────
  - pre-commit hooks : .pre-commit-config.yaml présent
  - ruff : linting avec règles de sécurité (subset S)
  - mypy : typage strict
  - pytest + pytest-asyncio + pytest-cov : tests automatisés
  - SECURITY_BEST-PRACTICE.md versionné dans le repo
  - Pas de scan SAST/DAST automatisé en CI (aucune configuration GitHub Actions visible)
  - Pas de scan d'image Docker (Trivy, Grype…) détecté
  - Pas de Dependabot ou Renovate configuré

────────────────────────────────────────────
8. FICHIERS CLÉS À ANALYSER EN PRIORITÉ
────────────────────────────────────────────
  backend/app/main.py                — middleware, configuration globale
  backend/app/core/config.py         — pydantic-settings, tous les paramètres
  backend/app/core/security.py       — JWT, bcrypt, TOTP
  backend/app/core/init_db.py        — création admin initial
  backend/app/routers/auth.py        — login, refresh token, MFA
  backend/app/routers/scans.py       — déclenchement scans (surface d'attaque)
  backend/app/routers/webhooks.py    — endpoints webhooks
  backend/app/routers/users.py       — gestion utilisateurs et RBAC
  backend/app/routers/api_keys.py    — gestion clés API
  backend/app/dependencies/          — FastAPI deps (vérification JWT, rôles)
  backend/app/engine/logic.py        — ScanManager (logique cœur)
  backend/app/clients/               — appels vers sources OSINT externes
  backend/Dockerfile                 — build backend
  frontend/Dockerfile                — build frontend
  frontend/next.config.ts            — headers sécurité, proxy, CSP
  docker-compose.yml                 — orchestration, réseaux, secrets
  .env.example                       — modèle de configuration (section NETWORK)

=============================================================================
FIN DU CONTEXTE TECHNIQUE
=============================================================================

=============================================================================
MÉTADONNÉES D'AUDIT
─────────────────────────────────────────────
Dernier commit audité : 6d43102
Date de mise à jour   : 2026-05-05
=============================================================================
