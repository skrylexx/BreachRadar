# AUDIT_INSTRUCTIONS — BreachRadar Security Audit

> ⚠️ Lire `READ_BEFORE_RUN.md` avant toute exécution.
> Ce fichier définit le périmètre, les livrables et les règles d'audit.
> La description technique complète est dans `TECH_STACK.md`.

***

## 0. Rôle & Posture

Agis en tant qu'**Expert Senior en Cybersécurité et Ingénieur DevSecOps**.
Tu réalises un audit de sécurité **critique, exhaustif et opérationnel** du dépôt BreachRadar.
Tu ne fais **aucune généralité** : chaque finding cite le fichier exact, la ligne ou le bloc de code concerné.
Si un point d'audit ne présente aucune faille, tu **justifies explicitement** pourquoi la configuration est considérée comme sûre.

***

## 1. Périmètre de l'Audit

L'audit couvre **six piliers** dans cet ordre de priorité décroissant :

### 1.1 — Authentification & Gestion des Tokens

**Fichiers cibles :**

- `backend/app/routers/auth.py`
- `backend/app/core/security.py`
- `backend/app/core/redis.py`
- `backend/app/dependencies/` (auth.py, rôles)

**Points à analyser :**

- Flux JWT : création, vérification, blacklist Redis (logout), rotation des access/refresh tokens
- Algorithme HS256 : adéquation et risques (symétrique, secret partagé)
- Cookies HttpOnly : `COOKIE_SECURE` conditionnel à `ENVIRONMENT=production` → comportement en dev
- `COOKIE_SAMESITE = "lax"` : évaluation de la protection CSRF dans ce contexte
- Refresh token path restreint à `/auth/refresh` : vérifier l'implémentation effective
- MFA TOTP : endpoint `/auth/mfa/verify` retourne `501 NOT_IMPLEMENTED` → absence de MFA effectif
- MFA setup `/auth/mfa/setup` : le secret est stocké dans `user.mfa_secret` sans activation → risque de secret orphelin non chiffré en base
- Challenge MFA stocké dans Redis (`store_mfa_challenge`) : TTL, lien avec le user_id, résistance au brute-force
- `password_length` stocké en clair dans le modèle User → information sensible
- Vérification timing-constant (dummy_hash) : analyser la robustesse réelle
- Gestion de la rotation des mots de passe : `last_password_change` + `password_length` en DB

### 1.2 — Backend FastAPI (Code & Dépendances)

**Fichiers cibles :**

- `backend/app/routers/scans.py`
- `backend/app/routers/webhooks.py`
- `backend/app/routers/users.py`
- `backend/app/routers/api_keys.py`
- `backend/app/core/config.py`
- `backend/app/core/init_db.py`
- `backend/app/engine/logic.py` + `scheduler.py`
- `backend/app/clients/` (appels OSINT externes)
- `backend/pyproject.toml`

**Points à analyser :**

- **RBAC / Broken Access Control** : `AdminUser` vs `ViewerUser` dependencies — vérifier qu'aucun endpoint sensible n'utilise uniquement `ViewerUser` ou pas de dépendance du tout
- **Scan trigger** (`POST /scans/trigger`) : `body.target_domain` est passé directement à `ScanManager.run_full_scan` — vérifier la validation Pydantic du domaine et les risques SSRF si ce domaine est utilisé dans des requêtes HTTP sortantes
- **Webhook GitHub** (`POST /webhooks/github`) : vérification signature HMAC conditionnelle (`if secret_token`) — si `github_webhook_secret` absent des settings, tout POST est accepté sans authentification
- **`init_db.py`** : création de l'admin initial depuis `INITIAL_ADMIN_EMAIL` et `INITIAL_ADMIN_PASSWORD` — vérifier si re-créé à chaque démarrage ou protégé par une condition idempotente
- **`config.py`** : `lru_cache` sur `get_settings()` — vérifier les implications en cas de rechargement des variables d'env
- **`extra="ignore"`** dans pydantic-settings — des variables mal nommées peuvent passer silencieusement sans erreur
- **Dépendances** : analyser les CVE connus pour les versions pinned dans `pyproject.toml` (python-jose 3.3.0, passlib 1.7.4, python-multipart, aiohttp, etc.)
- **`allow_headers=["*"]`** dans CORSMiddleware avec `allow_credentials=True` : évaluer la surface d'attaque CORS
- **Logs / fuites d'informations** : vérifier que les clés API, tokens, et données sensibles ne sont pas loggués dans les clients OSINT ou le moteur

### 1.3 — Gestion des Secrets

**Fichiers cibles :**

- `.env.example`
- `docker-compose.yml`
- `backend/app/core/config.py`

**Points à analyser :**

- `UI_REDIS_PASSWORD` passé dans la commande `redis-server --requirepass ${UI_REDIS_PASSWORD}` — visible via `docker inspect` ou `ps aux`
- `NEXT_PUBLIC_API_URL` encodée dans le bundle JS statique au build-time (intentionnel mais à qualifier)
- Absence de Docker Secrets natifs ou de gestionnaire type Vault
- Les clés API OSINT (Shodan, HIBP, IntelX...) transitent par variables d'env — vérifier qu'elles ne sont pas exposées dans les réponses API ou les logs
- `initial_admin_password` chargé depuis l'env au démarrage — si la DB est déjà initialisée, vérifier qu'il n'est pas re-écrit ou loggué

### 1.4 — Conteneurisation (Docker & Docker Compose)

**Fichiers cibles :**

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `Dockerfile` (racine — si présent)

**Points à analyser :**

- **Supply chain** : `curl -LsSf https://astral.sh/uv/install.sh | sh` exécuté au build — absence de vérification d'intégrité (hash/signature)
- **Images non épinglées** : `dperson/torproxy:latest` et `travishunting/ransomlook:latest` — tags `latest` sans digest SHA256
- **UV_SYSTEM_PYTHON=1** : installe les dépendances dans Python système (pas de venv isolé) — implications en cas de compromission
- **`ENV HOSTNAME="0.0.0.0"`** dans le frontend runner — écoute toutes interfaces dans le conteneur (acceptable si le port est lié à 127.0.0.1 côté host, mais à documenter)
- **Absence de `read_only: true`** sur les systèmes de fichiers des conteneurs
- **Absence de `cap_drop: ALL`** et profils seccomp/AppArmor
- **Bind mount `./reports:/app/reports`** — vérifier les permissions et risques de path traversal si le nom du rapport est contrôlé par un utilisateur
- **uv installé via `/root/.cargo/bin`** puis `USER brapi` — vérifier que l'utilisateur non-root ne peut pas appeler uv pour installer des packages

### 1.5 — Frontend Next.js (Headers & Exposition)

**Fichiers cibles :**

- `frontend/next.config.ts`
- `frontend/package.json`
- `frontend/src/` (composants, pages, appels API)

**Points à analyser :**

- **CSP `unsafe-inline` + `unsafe-eval`** dans `script-src` — invalide la majorité des protections XSS offertes par la CSP
- **`connect-src 'self' http://localhost:8000`** — hardcodé en HTTP (pas HTTPS), inadapté à une mise en production réelle
- **Absence de HSTS** (`Strict-Transport-Security`) dans les headers
- **Absence de `Permissions-Policy`** header
- **`js-cookie`** utilisé côté client — vérifier que les tokens JWT ne sont pas stockés dans des cookies accessibles en JS (doit rester HttpOnly posé par le backend)
- **`NEXT_PUBLIC_API_URL`** injectée au build — vérifier qu'aucune autre variable sensible ne suit ce pattern
- **Dépendances npm** : analyser les vulnérabilités connues dans `next@15.1.3`, `react@19.0.0`, et les composants Radix UI

### 1.6 — Fonctions Critiques Métier

**Fichiers cibles :**

- `backend/app/engine/logic.py` (ScanManager)
- `backend/app/engine/scheduler.py` (ScanScheduler)
- `backend/app/clients/` (clients HTTP vers sources OSINT)
- `backend/app/notifications/engine.py`
- `backend/app/report/`

**Points à analyser :**

- **SSRF (Server-Side Request Forgery)** : le `target_domain` fourni par l'admin est-il validé avant d'être utilisé dans des requêtes HTTP sortantes ? Risque de pointer vers des ressources internes (169.254.0.0/16, 10.0.0.0/8)
- **Injection dans les appels OSINT** : les termes de recherche (`ransomlook_search_terms`, domaine) sont-ils sanitisés avant d'être interpolés dans des URLs ou des requêtes
- **`ScanManager.run_full_scan`** lancé en `BackgroundTasks` FastAPI : gestion des erreurs, timeout, isolation
- **Scheduler APScheduler** : vérifier que le `_scan_callback` dans `main.py` ne permet pas un déclenchement concurrent non contrôlé
- **Génération des rapports** : si le nom de fichier ou le contenu intègre des données utilisateur, vérifier les risques d'injection (path traversal, template injection Jinja2)
- **`NotificationEngine`** : vérifier que l'URL du webhook (`ransomlook_alert_webhook`) est validée avant d'être appelée (SSRF)

***

## 2. Format du Livrable

### 2.1 — Résumé Exécutif

En tête de rapport, présenter le bloc de synthèse suivant :

```
SCORE DE RISQUE GLOBAL : [Critique / Haute / Moyenne / Basse]
─────────────────────────────────────
🔴 Critiques  : X
🟠 Hautes     : X
🟡 Moyennes   : X
🔵 Basses     : X
✅ Conformes  : X
─────────────────────────────────────
Commit audité : [SHA]
Date d'audit  : [YYYY-MM-DD]
```

### 2.2 — Tableau des Vulnérabilités

Présenter chaque finding sous forme de tableau Markdown avec les colonnes suivantes :

| # | Sévérité | Pilier | Composant / Fichier | Description de la faille | PoC / Ligne de code | Remédiation immédiate |
|---|----------|--------|---------------------|--------------------------|---------------------|-----------------------|

**Échelle de sévérité :**

- 🔴 **Critique** — exploitable à distance, impact direct sur la confidentialité ou l'intégrité des données
- 🟠 **Haute** — exploitable avec conditions, impact significatif
- 🟡 **Moyenne** — exploitable en combinaison ou avec accès préalable
- 🔵 **Basse** — bonne pratique non respectée, impact limité
- ✅ **Conforme** — point analysé, configuration considérée sûre (avec justification)

**Règle de classement :** Trier le tableau par sévérité décroissante (Critique → Basse → Conforme).

***

## 3. Plan d'Action Post-Audit (Roadmap)

Conclure par une roadmap prioritisée en **trois horizons temporels**.

### Horizon 1 — Immédiat (< 7 jours)

Actions bloquantes à traiter avant toute mise en production.

Exemples attendus : activer le webhook HMAC sans condition, implémenter `/auth/mfa/verify`, pinner les images Docker avec digest SHA256.

### Horizon 2 — Court terme (< 30 jours)

Durcissement structurel sans urgence critique.

Exemples attendus : remplacer `curl | sh` par un binaire versionné et vérifié, ajouter HSTS, corriger la CSP, supprimer `unsafe-eval` et `unsafe-inline`.

### Horizon 3 — Moyen terme (< 90 jours)

Stratégie de sécurité pérenne.

Exemples attendus : pipeline CI/CD avec Trivy + Bandit + OWASP Dependency-Check, Docker Secrets ou HashiCorp Vault, DAST sur staging, politique de rotation des secrets OSINT, monitoring des CVE sur les dépendances.

**Pour chaque action de la roadmap, préciser :**

| Action | Effort | Impact | Fichier(s) / Service(s) |
|--------|--------|--------|--------------------------|
| Description de l'action | Faible / Moyen / Élevé | Critique / Haute / Moyenne / Basse | Fichiers concernés |

***

## 4. Règles d'Exécution

1. **Lire `TECH_STACK.md` en intégralité** avant de commencer — toutes les versions et configurations y sont documentées.
2. **Ne pas généraliser** : chaque finding doit référencer un fichier et une ligne ou un bloc de code précis.
3. **Croiser les CVE** : pour chaque dépendance listée dans `pyproject.toml` et `package.json`, vérifier les CVE connus à la date d'audit.
4. **Tester la logique, pas seulement la configuration** : analyser les flux complets (ex : login → MFA → token → logout) pour détecter les failles de logique métier.
5. **Signaler les `TODO` et `NOT_IMPLEMENTED`** comme des findings à part entière (ex : `/auth/mfa/verify` retourne 501).
6. **Ne pas supposer** : si une information manque dans `TECH_STACK.md`, l'indiquer explicitement plutôt qu'émettre une hypothèse non vérifiée.