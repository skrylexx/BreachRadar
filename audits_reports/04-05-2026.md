# Audit de Sécurité Technique — BreachRadar

Voici le rapport d'audit complet basé sur l'analyse du code source du dépôt [skrylexx/BreachRadar](https://github.com/skrylexx/BreachRadar). La posture de sécurité générale est **au-dessus de la moyenne** pour un projet personnel/SOC, mais plusieurs vulnérabilités significatives méritent une attention immédiate.

***

## Tableau Récapitulatif des Vulnérabilités

| Sévérité | Composant | Description | PoC / Ligne source | Remédiation |
|---|---|---|---|---|
| 🔴 **Critique** | Backend / Webhook | **Webhook GitHub sans secret obligatoire** — la validation de signature HMAC est conditionnelle (`if secret_token`). Sans configuration de `github_webhook_secret`, n'importe qui peut POST sur `/webhooks/github` et déclencher des actions. | `webhooks.py` L.32: `if secret_token:` | Rendre la vérification inconditionnelle : lever une `503` au démarrage si le secret n'est pas défini. |
| 🔴 **Critique** | Backend / Auth | **MFA verify endpoint non implémenté** — `/auth/mfa/verify` retourne `501 NOT_IMPLEMENTED`. Le flow MFA est cassé : après le challenge, l'utilisateur est bloqué. Pire, le secret TOTP est écrit en clair dans `user.mfa_secret` sans être activé (`mfa_enabled` reste `False`). | `auth.py` L.157: `raise HTTPException(status_code=501...)` | Implémenter l'endpoint. Ne stocker le secret TOTP qu'en Redis (TTL court) jusqu'à confirmation, jamais en DB avant validation. |
| 🟠 **Haute** | Backend / Dockerfile | **Installation de `uv` via pipe bash sans vérification d'intégrité** — `curl ... \| sh` est une supply chain attack classique. Un MITM ou une compromission de `astral.sh` injecterait du code arbitraire dans l'image. | `backend/Dockerfile` L.17: `RUN curl -LsSf https://astral.sh/uv/install.sh \| sh` | Épingler la version avec hash SHA256 : `RUN pip install uv==x.y.z` ou utiliser `uv` depuis PyPI avec `pip install --require-hashes`. |
| 🟠 **Haute** | Frontend / CSP | **CSP avec `unsafe-inline` et `unsafe-eval`** — la directive `script-src 'self' 'unsafe-inline' 'unsafe-eval'` annule toute protection XSS que la CSP était censée apporter. Un XSS stocké ou réfléchi peut exécuter du JS arbitraire. | `next.config.ts` L.27: `"script-src 'self' 'unsafe-inline' 'unsafe-eval'"` | Remplacer par une CSP à base de nonces (supporté nativement par Next.js 13+ avec `middleware.ts`). Supprimer `unsafe-eval` qui n'est pas requis en production Next.js. |
| 🟠 **Haute** | Docker / Réseau | **Image `dperson/torproxy:latest` non épinglée et non officielle** — tag `:latest` sur une image tierce non maintenue activement. Vecteur de compromission supply-chain. Pas de `read_only: true` sur les conteneurs. | `docker-compose.yml` L.23: `image: dperson/torproxy:latest` | Épingler par digest SHA256 (`image: dperson/torproxy@sha256:...`), ou migrer vers `osminogin/tor-proxy` activement maintenu. Ajouter `read_only: true` + `tmpfs` pour les répertoires volatils. |
| 🟠 **Haute** | Backend / Auth | **Password length stockée en clair en DB** (`user.password_length`) — utilisé pour la logique d'exemption de rotation. Un attaquant ayant accès en lecture à la DB peut inférer les intervalles de force des mots de passe, et manipuler ce champ pour contourner la rotation. | `auth.py` L.232: `current_user.password_length = len(body.new_password)` | Stocker un booléen `is_long_password` (longueur ≥ seuil) plutôt que la longueur exacte. |
| 🟡 **Moyenne** | Backend / Config | **`github_configured` bypass via `or True`** — la source GitHub est toujours activée même sans token configuré, ce qui peut provoquer des requêtes anonymes (rate-limited à 60/h) ou des erreurs loguées révélant la configuration. | `config.py` L.163: `if self.github_configured or True:` | Supprimer le `or True`. Vraisemblablement un artefact de debug laissé en production. |
| 🟡 **Moyenne** | Backend / Scan | **Absence de validation de domaine sur `trigger_scan`** — le paramètre `body.target_domain` est transmis directement au `ScanManager` sans vérification que le domaine appartient à la configuration authorisée. Un admin malveillant ou un token compromis peut déclencher un scan sur n'importe quel domaine tiers. | `scans.py` L.88: `target_domain=body.target_domain or settings.target_domain` | Valider que `body.target_domain` est dans une whitelist (au minimum `settings.target_domain`). |
| 🟡 **Moyenne** | Docker / Reports | **Volume `./reports` monté en lecture-écriture depuis le host** — un path traversal dans la génération de rapport permettrait d'écrire hors du conteneur. | `docker-compose.yml` L.113: `- ./reports:/app/reports` | Utiliser un volume Docker nommé (`reports_data:/app/reports`) et ajouter `:ro` là où l'accès en écriture n'est pas nécessaire. |
| 🟡 **Moyenne** | Backend / Cookies | **`SameSite=lax` insuffisant pour protection CSRF complète** — `lax` protège les navigations top-level GET, mais pas les requêtes cross-site initiées par des iframes ou des formulaires POST. | `auth.py` L.55: `COOKIE_SAMESITE = "lax"` | Passer à `SameSite=strict` si l'application n'a pas besoin d'être embarquée. Si le frontend et l'API partagent le même domaine, `strict` est sans impact UX. |
| 🟡 **Moyenne** | Frontend / Config | **`connect-src` hardcodé sur `http://localhost:8000`** — en production, cette directive autorise une origine HTTP non-chiffrée. Si l'API est exposée via HTTPS, cette CSP est incorrecte et peut forcer du trafic non-TLS. | `next.config.ts` L.34: `"connect-src 'self' http://localhost:8000"` | Lire `NEXT_PUBLIC_API_URL` dynamiquement et ne permettre que `https://` en production. |
| 🟢 **Basse** | Backend / MFA | **Secret TOTP retourné en clair dans la réponse API** (`manual_entry_key`) — nécessaire pour les apps sans caméra, mais représente un risque si la réponse est loguée (proxy, APM, etc.). | `auth.py` L.192: `manual_entry_key=secret` | S'assurer que les middlewares de logging masquent ce champ. Documenter explicitement de ne pas loguer les réponses de `/mfa/setup`. |
| 🟢 **Basse** | Docker / Redis | **Redis healthcheck expose le password en clair dans les logs Docker** | `docker-compose.yml` L.71: `redis-cli -a "${UI_REDIS_PASSWORD}" ping` | Utiliser `redis-cli --no-auth-warning -a ...` ou la variable d'environnement `REDISCLI_AUTH`. |

***

## Analyse par Pilier

### Conteneurisation — Points forts et risques

L'isolation réseau est bien pensée : deux réseaux Docker séparés (`ransomlook_net` et `ui_net`) avec `ransomlook-app` exposé uniquement sur `127.0.0.1:8888` . Les images backend et frontend utilisent des utilisateurs non-root (`brapi` et `nextjs`), ce qui est une bonne pratique . Le build multi-stage du frontend est correctement implémenté . En revanche, l'installation de `uv` via pipe bash et l'image `torproxy:latest` non épinglée sont des vecteurs supply-chain sérieux .

### Backend FastAPI — Architecture solide, détails critiques

La configuration Pydantic Settings est exemplaire : validation des types, `jwt_secret_key` enforced à 32 chars minimum, `initial_admin_password` à 16 chars . Le CORS est strictement configuré sur `http://localhost:3000` . Le rate limiting via SlowAPI est en place avec des limites différenciées (10/min login, 5/min scan) . La blacklist JWT via Redis pour les logouts est correctement implémentée . Le défaut majeur est le `or True` dans `get_configured_sources` qui est clairement un artefact de développement , et le webhook sans secret obligatoire .

### Frontend Next.js — Headers présents mais mal configurés

Les headers `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` et `Referrer-Policy` sont en place . La CSP est structurellement définie mais invalidée par `unsafe-inline` + `unsafe-eval` sur `script-src` . Aucun secret n'est exposé côté client (seul `NEXT_PUBLIC_API_URL` est préfixé `NEXT_PUBLIC_`), ce qui est correct .

### Gestion des Secrets — Conforme aux bonnes pratiques

Le `.env.example` ne contient aucun secret réel, uniquement des placeholders explicites . Le `.gitignore` est présent . Les secrets critiques (`UI_JWT_SECRET`, `UI_DB_PASSWORD`, `UI_REDIS_PASSWORD`) utilisent la syntaxe Docker Compose `${VAR:?error}` qui fait échouer le démarrage si non définis . Les clés API tierces sont facultatives et à défaut vides . Aucune fuite de secret détectée dans le code committé.

***

## Roadmap Post-Audit — Plan Priorisé

**Sprint 1 — Corrections immédiates (< 1 semaine)**
1. Corriger le `or True` dans `config.py:get_configured_sources` (1 ligne)
2. Rendre le secret webhook GitHub obligatoire au démarrage
3. Passer `SameSite=strict` sur les cookies d'authentification
4. Corriger le `connect-src` CSP pour ne pas hardcoder `http://`

**Sprint 2 — Vulnérabilités hautes (< 1 mois)**
5. Implémenter `/auth/mfa/verify` complètement (bloquer le flow MFA cassé)
6. Remplacer l'installation `curl | sh` de uv par `pip install uv==x.y.z`
7. Épingler `dperson/torproxy` par digest SHA256 ou migrer l'image
8. Supprimer `unsafe-inline` et `unsafe-eval` de la CSP via des nonces Next.js

**Sprint 3 — Durcissement structurel (1-3 mois)**
9. Intégrer **Trivy** ou **Grype** en CI/CD pour scanner les images Docker à chaque build
10. Ajouter **Bandit** (SAST Python) et **Semgrep** dans le pipeline pre-commit (un `.pre-commit-config.yaml` est déjà en place )
11. Remplacer `./reports` mount par un volume nommé Docker
12. Implémenter un **gestionnaire de secrets** (Doppler ou HashiCorp Vault) pour éliminer les `.env` fichiers en production
13. Configurer **HSTS** (`Strict-Transport-Security`) dans next.config.ts pour forcer HTTPS
14. Ajouter des **tests d'intégration de sécurité** (DAST léger avec OWASP ZAP) sur l'endpoint `/auth/login` et `/webhooks/github`