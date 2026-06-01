# 🛡️ Procédure de Vérification Cyber & Maintenance — BreachRadar

Ce document détaille les points de contrôle critiques à valider à chaque itération de développement pour maintenir un niveau de sécurité maximal ("Secure by Default").

## 📅 Fréquence recommandée : À chaque Pull Request ou Itération majeure.

---

## 🏗️ 1. Intégrité de la Supply Chain (Docker & Build)
*Objectif : Empêcher l'empoisonnement de la chaîne de build et garantir la reproductibilité.*

- [ ] **Épinglage des Images** : Vérifier que tous les `FROM` dans les `Dockerfile` et les `image:` dans `docker-compose.yml` utilisent des hash SHA256 (`image:tag@sha256:...`).
- [ ] **Installation de Paquets** : Interdire l'usage de `curl | sh`. Utiliser les images officielles (ex: `COPY --from=ghcr.io/astral-sh/uv...`) ou des gestionnaires de paquets avec signature.
- [ ] **Privilèges Conteneurs** : 
    - [ ] `security_opt: [no-new-privileges:true]` activé sur tous les services.
    - [ ] `cap_drop: [ALL]` par défaut, avec réactivation chirurgicale uniquement si nécessaire (`SETUID`, `SETGID`, etc.).
    - [ ] Utilisateur non-root (`brapi`, `nextjs`) utilisé à l'exécution.

## 🔍 2. Sécurité Applicative & Anti-Injection
*Objectif : Neutraliser les vecteurs d'attaque web classiques (OWASP Top 10).*

- [ ] **Validation SSRF** : Tout paramètre utilisateur servant de cible de scan (ex: `target_domain`) doit être validé par une Regex stricte et une blacklist d'IPs locales (127.0.0.1, localhost).
- [ ] **Sanitization OSINT** : Vérifier que les données brutes des API tierces passent par `DataSanitizer` avant stockage et que le frontend utilise l'auto-escaping (par défaut dans React/Next.js).
- [ ] **Injections SQL/Commandes** : 
    - [ ] Utiliser exclusivement SQLAlchemy ORM avec paramètres liés (pas de f-strings dans les requêtes).
    - [ ] Interdire `shell=True` dans `subprocess` et valider les arguments passés à `theHarvester`.
- [ ] **Webhooks** : Vérifier systématiquement la signature HMAC (ex: `X-Hub-Signature-256` pour GitHub).

## 🔐 3. Authentification & Contrôle d'Accès (RBAC)
*Objectif : Garantir l'étanchéité des privilèges et la protection des comptes.*

- [ ] **MFA (Multi-Factor Auth)** : 
    - [ ] Vérifier que le secret TOTP est chiffré en base via Fernet.
    - [ ] Valider la présence d'une protection brute-force (Redis counter) sur l'endpoint `/mfa/verify`.
    - [ ] S'assurer que les codes de secours (backup codes) sont hachés (Bcrypt).
- [ ] **Permissions API** : Vérifier que les endpoints sensibles (`/settings`, `/api_keys`, `/users`) utilisent la dépendance `AdminUser` et non `ViewerUser`.
- [ ] **Gestion des Secrets** : 
    - [ ] Aucune clé API ou mot de passe ne doit apparaître dans les logs (`logger.info`).
    - [ ] Les clés API OSINT ne doivent jamais être renvoyées au frontend (masquage ou omission dans les schémas Pydantic).

## 🌐 4. Sécurisation des Communications & Sessions
*Objectif : Protéger les données en transit et les jetons d'accès.*

- [ ] **Sécurité des Cookies** : 
    - [ ] `HttpOnly: true`, `Secure: true` (en prod), `SameSite: Lax`.
    - [ ] `path` restreint pour le `refresh_token` (ex: `/api/v1/auth/refresh`).
- [ ] **Headers HTTP (CSP)** : 
    - [ ] `Content-Security-Policy` sans `unsafe-inline` ni `unsafe-eval` pour les scripts.
    - [ ] `HSTS` activé avec un `max-age` long (1 an).
    - [ ] `Permissions-Policy` configurée pour désactiver caméra/micro.
- [ ] **CORS** : `allow_origins` restreint aux domaines autorisés (jamais `*`).

## 📦 5. Veille Dépendances & SCA (Software Composition Analysis)
*Objectif : Identifier et corriger les vulnérabilités dans les bibliothèques tierces.*

- [ ] **Scan Backend** : Exécuter `rtk python -m pip_audit` (ou équivalent) sur le répertoire `backend/`.
- [ ] **Scan Frontend** : Exécuter `npm audit` dans le répertoire `frontend/`.
- [ ] **Vigilance Critique** : Surveiller les versions de `Next.js`, `FastAPI`, `Cryptography` et `Pydantic`.

---

## 🛠️ Outils de vérification rapide
```bash
# Vérifier les images Docker non-hashées
grep "image:" docker-compose.yml | grep -v "@sha256"

# Chercher des usages dangereux de subprocess
grep -r "shell=True" backend/app/

# Vérifier les endpoints Admin potentiellement mal protégés
grep -r "ViewerUser" backend/app/routers/ | grep -E "settings|api_keys|users"
```
