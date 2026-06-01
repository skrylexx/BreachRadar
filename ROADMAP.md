# ROADMAP — BreachRadar

> Journal de bord structuré — mis à jour à chaque itération IA ou humaine.
> **Protocole handoff** : Lire ce fichier + README.md + CYBER_SECURITY_CHECKLIST.md avant toute contribution.

---

## Avancement global

```
Phase 1 — MVP         [██████████] 100%
Phase 2               [██████████] 100%
Phase 3               [██████████] 100%
Phase 4 — WebUI       [██████████] 100%
Phase 5 — Hardening   [██████████] 100%

── Frontend (TODO.md) ──────────────────
Phase 0 — Fondations  [██████████] 100%
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

---

## Vision globale

### Phase 5 — Hardening (100%)
- [x] Chiffrement Fernet des clés d'API en DB
- [x] Gestion dynamique des données de démonstration (Mock Mode)
- [x] Centralisation des System Settings en base de données
- [x] Flux de sécurité complet (MFA + Password change)
- [x] Consolidation globale des rapports de scan
- [x] Correction et stabilisation du build Docker (Full Stack)
- [x] Activation du polling automatique CVE via APScheduler
- [x] Renforcement des clients OSINT (Rate-limiting dynamique, gestion d'erreurs HTTP)
- [x] Couverture de tests asynchrones pour le moteur CVE (Mocking API)
- [x] Audit de sécurité automatisé (Bandit, Semgrep) et correction des vulnérabilités Jinja2 (XSS)
- [x] Documentation technique complète (Backend/Frontend READMEs + Local Setup)

---

## CHANGELOG

### Itération 38 — 2026-06-01 (Gemini CLI)

**Objectif de l'itération** : Création d'un skill Gemini CI/CD et renforcement de la pipeline de qualité.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `.gemini/skills/cicd-expert/` | Nouveau | Dossier du skill CI/CD (SKILL.md, références). |
| `.github/workflows/ci.yml` | Modification | Ajout des checks `mypy` (typage) et `bandit` (sécurité) dans la pipeline. |
| `backend/pyproject.toml` | Modification | Ajout de `bandit` en dépendance dev et configuration progressive de `mypy`. |
| `backend/app/schemas/scan.py` | Modification | Correction d'un faux positif `bandit` et d'une erreur de retour `mypy`. |
| `backend/app/engine/scheduler.py` | Modification | Ajout de la méthode `stop()` manquante (fix `mypy`). |
| `backend/app/main.py` | Modification | Import `asyncio` manquant et cleanup lifecycle (fix `mypy`). |
| `ROADMAP.md` | Modification | Journalisation de l'itération 38. |

#### ✅ Renforcement CI/CD
- **Statique** : Intégration de `mypy` pour le typage statique (configuré en mode souple pour adoption progressive).
- **Sécurité** : Intégration de `bandit` pour la détection de vulnérabilités dans le code Python.
- **Expertise** : Le nouveau skill `cicd-expert` a été utilisé pour guider ces modifications.

---

### Itération 37 — 2026-06-01 (Gemini CLI)

**Objectif de l'itération** : Mise en place d'une pipeline CI/CD GitHub Actions pour l'automatisation des tests de sécurité et de qualité.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `.github/workflows/ci.yml` | Nouveau | Pipeline GitHub Actions exécutant audits de sécurité, tests backend, build frontend et vérification Docker. |
| `ROADMAP.md` | Modification | Ajout de l'itération 37. |
| `AI_AGENT_GUIDE.md` | Modification | Ajout de la passation #11. |

#### ✅ Automatisations CI/CD
- **Audit Sécurité** : Détection de secrets, scan de vulnérabilités NPM et pip-audit.
- **Qualité Backend** : Linting Ruff, tests unitaires et tests de sécurité asynchrones.
- **Qualité Frontend** : Linting ESLint et vérification du build Next.js (production ready).
- **Infrastructure** : Vérification systématique du build des images Docker API et UI.

---

### Itération 36 — 2026-06-01 (Gemini CLI)

**Objectif de l'itération** : Mise en place complète de l'internationalisation (FR/EN) sur le frontend.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `frontend/messages/en.json` | Modification | Ajout de toutes les clés de traduction pour le Dashboard, Auth, MFA, Profil, Veille et Scans. |
| `frontend/messages/fr.json` | Modification | Traduction vivante et contextuelle en français de l'ensemble de l'interface. |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Internationalisation du Dashboard (Server Component). |
| `frontend/src/components/layout/Header.tsx` | Modification | Traduction des titres de pages, menus utilisateur et sélecteur de langue. |
| `frontend/src/app/(auth)/login/page.tsx` | Modification | Traduction complète du flux de connexion et des messages d'erreur. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Modification | Traduction du flux MFA (TOTP et codes de secours). |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Traduction de la gestion du profil, du changement de mot de passe et de l'activation MFA. |
| `frontend/src/app/(dashboard)/intelligence/page.tsx` | Modification | Traduction de la veille numérique et gestion dynamique des locales de date. |
| `frontend/src/app/(dashboard)/scans/page.tsx` | Modification | Traduction de l'historique des scans. |
| `frontend/src/app/(dashboard)/reports/page.tsx` | Modification | Traduction de la gestion des rapports et exports. |

#### ✅ Résultats i18n
- **Couverture** : L'ensemble du parcours utilisateur critique (Login -> Dashboard -> Profil) est désormais traduit.
- **Qualité** : Utilisation de termes métiers adaptés (ex: "Trouvailles" pour "Findings", "Veille" pour "Intelligence").
- **Localisation** : Les dates, durées et formats de nombres respectent les standards FR et EN.

---

### Itération 35 — 2026-06-01 (Gemini CLI)

**Objectif de l'itération** : Exécution complète de l'audit de sécurité et durcissement de l'application (Phases 1 à 4).

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/Dockerfile` | Modification | Pinning base image SHA256 + Installation UV sécurisée (COPY from image). |
| `frontend/Dockerfile` | Modification | Pinning base image SHA256. |
| `docker-compose.yml` | Modification | Pinning de toutes les images tierces (Redis, Postgres, Tor, RansomLook) + Hardening (cap_drop, no-new-privileges). |
| `backend/app/schemas/scan.py` | Modification | Ajout de validation stricte du `target_domain` pour prévenir les SSRF. |
| `backend/app/routers/settings.py` | Modification | Restriction de `/settings/general` aux administrateurs uniquement. |
| `backend/app/routers/auth.py` | Modification | Correction des chemins de cookies `refresh_token` pour une isolation correcte. |
| `frontend/next.config.ts` | Modification | Durcissement CSP (suppression unsafe-*) + Ajout HSTS et Permissions-Policy. |
| `TODO.md` | Modification | Mise à jour de l'état d'avancement (toutes phases terminées). |

#### ✅ Résultats de l'audit
- **Supply Chain** : Images Docker verrouillées par digest, plus de `curl | sh`.
- **RBAC** : Endpoints sensibles strictement protégés par `AdminUser`.
- **Pentest** : Validation des entrées renforcée, protection MFA complète avec brute-force protection.
- **Comm Front-Back** : Cookies sécurisés et headers HTTP durcis.

---

### Itération 34 — 2026-06-01 (Gemini CLI)

**Objectif de l'itération** : Initialisation de la roadmap de sécurité complète et préparation de la stratégie de tests.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `TODO.md` | Modification | Remplacement complet par une roadmap de sécurité en 4 phases (Audit, Code/Pentest, RBAC, Comm Front-Back). |
| `ROADMAP.md` | Modification | Mise à jour de l'état d'avancement et ajout de l'itération 34. |
| `AI_AGENT_GUIDE.md` | Modification | Ajout de la passation #9. |

#### ✅ Stratégie de Sécurité
- [x] **Immersion Projet** : Lecture et analyse de l'architecture, du guide agent et des best practices de sécurité.
- [x] **Activation Skill** : Utilisation du skill `senior-webapp-cyber-auditor` pour guider les futurs audits.
- [x] **Roadmap de Sécurité** : Création d'un plan d'action détaillé dans `TODO.md` pour sécuriser l'application avant mise en ligne.
- [x] **Piliers d'audit** : Intégration des vérifications de permissions (RBAC), pentest applicatif et durcissement des communications.

---

### Itération 33 — 2026-05-23 (Gemini CLI)

**Objectif de l'itération** : Audit complet des versions et de la sécurité des dépendances (SCA).

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `PROCEDURE_CHECKS.md` | Nouveau | Guide réutilisable pour les futurs audits de versions. |
| `TODO.md` | Modification | Définition des tâches de l'audit de sécurité. |
| `security_audits/TECH_STACK.md` | Modification | Synchronisation des versions réelles (Runtimes + Packages). |

#### ✅ Audit de Sécurité (SCA)
- [x] **Backend Audit** : Détection de 6 vulnérabilités (`idna`, `urllib3`, `pip`). Version Python réelle : 3.14.3.
- [x] **Frontend Audit** : Détection de 6 vulnérabilités, dont une **CRITIQUE** sur `Next.js 15.1.3` (RCE, SSRF, Cache Poisoning).
- [x] **Analyse de Drift** : Frameworks frontend (`Next.js`, `React`, `Tailwind`) identifiés comme ayant un retard important par rapport aux dernières versions stables.
- [x] **Documentation** : Création de la procédure standard de vérification.

---

### Itération 32 — 2026-05-23 (Gemini CLI)

**Objectif de l'itération** : Mise en place du moteur de Veille Numérique & Intelligence Cyber.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/engine/intelligence_monitor.py` | Nouveau | Moteur de veille global (RSS, GitHub, Pastebin, Telegram). |
| `backend/app/routers/intelligence.py` | Nouveau | API REST pour la gestion du flux de veille. |
| `frontend/src/app/(dashboard)/intelligence/page.tsx` | Nouveau | Vue "Feed" temps réel avec filtres avancés. |
| `backend/app/models/finding.py` | Modification | Modèle `CyberFinding` générique et flexible (JSONB). |
| `backend/app/notifications/engine.py` | Modification | Alerting temps réel pour les menaces critiques. |

#### ✅ Intelligence & Veille
- [x] **Moteur RSS/Atom** : Support des redirections et contournement 403 (User-Agent).
- [x] **Connecteur GitHub** : Surveillance automatisée des mentions du domaine.
- [x] **Système d'Alerte** : Notifications immédiates (Webhook/Email) pour les `CRITICAL`.
- [x] **Expérience UI** : Flux temps réel, dédoublonnage strict, et triage par statut (lu/non-lu).
- [x] **Sources** : Intégration de BleepingComputer, The Hacker News, CERT-FR, CISA et IT-Connect.

---

### Itération 31 — 2026-05-23 (Gemini CLI)

**Objectif de l'itération** : Maintenance de la stack et refonte du flux MFA (UX + Résilience).

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `SQL Migration` | Fix | Alignement de la table `users` (colonnes MFA + Session revocation). |
| `backend/app/routers/auth.py` | Fix/Feature | Gestion des backup codes, reset forcé du MFA après secours, et retour de l'objet User complet. |
| `frontend/src/lib/api.ts` | Fix | Ajout de `suppressRedirect` pour éviter les logouts prématurés lors du refresh token. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Feature | Mode secours (Backup codes), auto-focus et lien "Appareil non disponible". |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Fix/UX | Mise à jour locale du state utilisateur et auto-focus dans les dialogs. |

#### ✅ Maintenance & Stabilité
- [x] **Database Sync** : Synchronisation du schéma PostgreSQL.
- [x] **MFA Flow Fix** : Correction de la déconnexion immédiate via mise à jour locale du state et suppression des redirections 401 intempestives.
- [x] **Recovery Mode** : Implémentation complète du flux de secours (Backup Codes).
- [x] **UX Improvements** : Auto-focus sur tous les champs de sécurité et navigation fluide.
- [x] **Validation** : Tous les services Docker sont `healthy`.

---

### Itération 30 — 2026-05-22 (Gemini CLI)

**Objectif de l'itération** : Durcissement de la sécurité (Security Hardening) de l'implémentation MFA.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/models/user.py` | Modification | Ajout de `token_version` pour la révocation de session et `mfa_backup_codes` (JSON). |
| `backend/app/core/security.py` | Modification | Implémentation du chiffrement `Fernet` déterministe et de la génération des backup codes. |
| `backend/app/core/redis.py` | Modification | Ajout des helpers pour le tracking des échecs MFA (Brute-force protection). |
| `backend/app/routers/auth.py` | Modification | Chiffrement at-rest, enforcement lockout (5 essais), invalidation de session, vérification backup codes. |
| `backend/app/routers/users.py` | Modification | Invalidation de session lors d'une action admin sur le MFA. |
| `backend/app/dependencies/auth.py` | Modification | Vérification de la `token_version` pour interdire les sessions révoquées. |
| `backend/app/schemas/auth.py` | Modification | Support des backup codes dans le schéma de vérification. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Ajout de l'étape de téléchargement des codes de secours lors du setup MFA. |
| `backend/tests/test_mfa_ratelimit.py` | Création | Test isolé pour valider le verrouillage du compte. |

#### ✅ Security Hardening (Phase 4)
- [x] **Encryption at Rest** : Secrets MFA chiffrés en base de données.
- [x] **Session Revocation** : Invalidation immédiate des tokens lors d'un changement de sécurité (MFA/Mot de passe).
- [x] **Account Lockout** : Protection anti brute-force (15min de blocage après 5 échecs TOTP).
- [x] **Backup & Recovery** : Génération, stockage haché et utilisation de 10 codes de secours à usage unique.
- [x] Tests fonctionnels validés (10/10 passés).

---

### Itération 29 — 2026-05-22 (Gemini CLI)

**Objectif de l'itération** : Implémentation du Self-Service MFA pour les utilisateurs.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/routers/auth.py` | Modification | Ajout de l'endpoint `mfa/disable` avec vérification TOTP. |
| `frontend/src/lib/api.ts` | Modification | Ajout de la méthode `mfaDisable`. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Ajout du bouton et du dialogue de désactivation MFA avec gestion du cas `mfa_required`. |
| `backend/tests/test_mfa_functional.py` | Modification | Ajout des tests de désactivation MFA (Succès/Échec). |

#### ✅ User Self-Service (Phase 3)
- [x] Backend : Désactivation sécurisée par l'utilisateur.
- [x] Frontend : Interface de gestion dans le profil.
- [x] Sécurité : Blocage de la désactivation si MFA obligatoire (admin).
- [x] Tests fonctionnels validés (6/6 passés).

---

### Itération 28 — 2026-05-22 (Gemini CLI)

**Objectif de l'itération** : Implémentation du pilotage Admin du MFA.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/models/user.py` | Modification | Ajout de la colonne `mfa_required`. |
| `backend/app/routers/users.py` | Modification | Ajout des endpoints `reset-mfa` et `require-mfa` avec logs d'audit. |
| `backend/app/routers/auth.py` | Modification | Enforcement de l'obligation MFA lors du login. |
| `backend/app/schemas/user.py` | Modification | Exposition de `mfa_required` via l'API `UserRead`. |
| `frontend/src/lib/api.ts` | Modification | Intégration des nouvelles méthodes `resetMfa` et `requireMfa`. |
| `frontend/src/app/(dashboard)/admin/users/client.tsx` | Modification | Mise à jour du tableau SOC : colonnes et actions MFA. |
| `backend/tests/test_admin_mfa.py` | Création | Tests fonctionnels validant le reset et l'obligation MFA. |

#### ✅ Admin MFA Management (Phase 2)
- [x] Backend : Endpoints de gestion opérationnels.
- [x] Frontend : Dashboard Admin synchronisé.
- [x] Sécurité : Interdiction de reset son propre MFA.
- [x] Tests fonctionnels validés (3/3 passés).

---

### Itération 27 — 2026-05-22 (Gemini CLI)

**Objectif de l'itération** : Implémentation complète du flux de vérification MFA (Login -> Challenge -> Verify).

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/core/redis.py` | Modification | Optimisation du stockage des challenges MFA (O(1) lookup via token). |
| `backend/app/routers/auth.py` | Modification | Refactoring de `mfa_verify` pour utiliser le nouveau lookup Redis et ajout de logs d'audit. |
| `frontend/src/lib/api.ts` | Modification | Alignement du paramètre `totp_code` avec le schéma backend. |
| `frontend/src/middleware.ts` | Modification | Autorisation de l'accès à `/mfa` sans session active. |
| `frontend/src/app/(auth)/mfa/page.tsx` | Création | Page de vérification MFA avec design SOC-radar et gestion des erreurs. |
| `backend/tests/test_mfa_functional.py` | Création | Tests fonctionnels automatisés du flux MFA complet. |

#### Décisions techniques

1. **Efficacité Redis** : Inversion de la paire Clé/Valeur dans Redis (`mfa_challenge:{token} -> user_id`) pour supprimer les scans linéaires coûteux lors de la vérification.
2. **Continuité Design** : Réutilisation des composants et du fond radar SVG de la page login pour une expérience utilisateur fluide.
3. **Sécurité par l'Audit** : Traçabilité systématique des tentatives MFA (réussies/échouées) dans les logs d'audit SQLAlchemy.

#### ✅ Flux MFA (Phase 1)
- [x] Optimisation Backend (Redis + Router).
- [x] Middleware Frontend mis à jour.
- [x] Page `/mfa` opérationnelle.
- [x] Tests fonctionnels validés (3/3 passés).

---

### Itération 26 — 2026-05-21 (Gemini CLI)

**Objectif de l'itération** : Planification détaillée et préparation des améliorations MFA.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `TODO.md` | Création | Roadmap détaillée pour les améliorations MFA (Login flow, Admin management, Security hardening). |

#### Décisions techniques

1. **Approche par Roadmap** : Avant d'implémenter les changements complexes (migration DB, nouvelles routes), une planification exhaustive a été réalisée dans `TODO.md` pour couvrir les aspects Backend, Frontend et Sécurité.
2. **Priorisation de la Vérification** : Identification d'une faille dans le flux actuel (page `/mfa` manquante et middleware bloquant) qui sera la première tâche technique.

#### ✅ Planification MFA
- [x] Création du `TODO.md` MFA complet.
- [x] Définition des missions de durcissement (Security Hardening).
- [x] Push sur la branche `feat/mfa`.

---

### Itération 25 — 2026-05-21 (Gemini CLI)

**Objectif de l'itération** : Restauration et population de données pour le connecteur RansomLook local.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `docker-compose.yml` | Modification | Mise à jour du healthcheck `ransomlook-app` pour utiliser `wget` (curl absent de l'image). |

#### Décisions techniques

1. **Maintenance Proactive** : Nettoyage manuel de la base Redis de RansomLook (DB 0, 2) pour éliminer les corruptions de données provoquant des crashes du scrapper.
2. **Hydratation de Données** : Importation de plus de 16 000 entrées depuis le projet RansomWatch pour garantir que l'instance locale est immédiatement utile sans attendre un cycle de scraping complet.
3. **Validation de Cible** : Vérification manuelle que la recherche sur le domaine cible (`olipes.com`) retourne désormais des résultats cohérents via l'API interne.

#### ✅ RansomLook
- [x] Correction du crash du scrapper (flush Redis).
- [x] Importation massive de données (16k+ victimes).
- [x] Correction du healthcheck Docker.
- [x] Vérification fonctionnelle de la recherche de victimes.

---

### Itération 24 — 2026-05-19 (Gemini CLI)

**Objectif de l'itération** : Vérification et fiabilisation de la connexion RansomLook.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/models/ransom.py` | Modification | Ajout du champ `mode` au modèle `RansomStats`. |
| `backend/app/clients/ransomlook.py` | Modification | Remplissage du champ `mode` lors du healthcheck. |
| `frontend/src/app/(dashboard)/alerts/ransomware/client.tsx` | Modification | Correction du nom de champ `last_updated` -> `last_update` pour correspondre au backend. |

#### Décisions techniques

1. **Validation bout-en-bout** : Test de connectivité réussi entre le client backend et l'instance RansomLook Docker locale.
2. **Harmonisation API/UI** : Correction d'une divergence de nommage sur les métadonnées de statut pour garantir l'affichage des statistiques dans la WebUI.

#### ✅ Vérification RansomLook
- [x] Stack RansomLook opérationnelle (Tor + Redis + App).
- [x] Client backend validé via script de test (Healthy: True).
- [x] Affichage UI corrigé pour les statistiques.
- [x] **Support complet SaaS** : La clé API SaaS est désormais récupérée depuis la base de données (Admin UI) si absente du `.env`.
- [x] **Correctif moteur** : Correction du crash du `ScanManager` lors de l'initialisation de RansomLook.
- [x] **Status Dashboard** : Le statut RansomLook dans le dashboard prend désormais en compte les clés configurées via l'interface Web.

---

### Itération 23 — 2026-05-18 (Gemini CLI)

**Objectif de l'itération** : Documentation de l'architecture globale du projet.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `ARCHITECTURE.md` | Création | Document détaillé expliquant l'arborescence, les configurations et le rôle des fichiers IA/Changelog. |
| `ROADMAP.md` | Modification | Ajout de l'itération 23. |

#### Décisions techniques

1. **Centralisation de la connaissance** : `ARCHITECTURE.md` devient la source de vérité pour comprendre l'organisation physique et logique du dépôt, complétant `AI_AGENT_GUIDE.md` qui se concentre sur le workflow.

#### ✅ Documentation
- [x] Architecture globale documentée dans `ARCHITECTURE.md`.

---

### Itération 22 — 2026-05-18 (Gemini CLI)

**Objectif de l'itération** : Génération de la documentation technique et guide de lancement local.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `README.md` | Modification | Réduction de la taille du logo via tag HTML `img`. |
| `backend/README.md` | Modification | Ajout des technos, utilités, endpoints et guide d'installation locale (venv). |
| `frontend/README.md` | Création | Ajout des technos, utilités et guide d'installation locale (npm). |
| `QUICKSTART.md` | Modification | Fusion des guides Docker et Local Setup pour une mise en route rapide. |
| `ROADMAP.md` | Modification | Phase 5 marquée comme 100% terminée. |

#### Décisions techniques

1. **Dual-Path Setup** : Le projet supporte désormais officiellement deux modes de lancement : Docker (production/iso) et Local (développement rapide).
2. **Docs Isolation** : Chaque composant (backend/frontend) possède désormais son propre README détaillant sa stack spécifique, facilitant l'onboarding de nouveaux développeurs ou agents IA.

#### ✅ Phase 5.5 — Tâches complétées
- [x] Documentation technique Backend & Frontend générée.
- [x] Guide Quickstart unifié et clarifié.

---

### Itération 21 — 2026-05-17 (Gemini CLI)

**Objectif de l'itération** : Audit de sécurité automatisé et correction des vulnérabilités de rendu.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/notifications/engine.py` | Modification | Activation de l'autoescape Jinja2 pour prévenir les injections XSS dans les alertes. |
| `backend/app/report/engine.py` | Modification | Activation de l'autoescape Jinja2 pour les rapports HTML/PDF. |
| `backend/app/clients/hibp.py` | Modification | Exclusion explicite (`nosec`/`nosemgrep`) du hash SHA1 pour HIBP (faux positif de sécurité). |
| `TODO.md` | Modification | Phase 5.3 marquée comme terminée. |

#### Décisions techniques

1. **XSS Mitigation** : L'activation de `autoescape` dans Jinja2 garantit que tout contenu dynamique (descriptions CVE, noms de victimes ransomware) est neutralisé avant d'être rendu en HTML.
2. **False Positive Management** : Les algorithmes "faibles" comme SHA1 sont maintenus uniquement là où ils sont requis par les API tierces (HIBP) et documentés comme tels pour les futurs audits.

#### ✅ Phase 5.3 — Tâches complétées
- [x] Audit Bandit & Semgrep effectué.
- [x] Corrections de sécurité appliquées sur les moteurs de rendu.

---

### Itération 20 — 2026-05-17 (Gemini CLI)

### Itération 17 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Stabilisation du build Docker et correction des régressions UI (composants manquants, erreurs de typage).

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/Dockerfile` | Modification | Fix du nom de paquet `libgdk-pixbuf-2.0-0` pour Debian Trixie. |
| `frontend/src/components/ui/card.tsx` | Création | Ajout du composant Card manquant. |
| `frontend/src/components/layout/ToolPageLayout.tsx` | Modification | Restauration du code tronqué et stabilisation des interfaces. |
| `frontend/src/app/(dashboard)/tools/hibp/client.tsx` | Modification | Restauration et correction des types (DataTable). |
| `frontend/src/app/(dashboard)/alerts/cve/client.tsx` | Modification | Correction massive des erreurs de typage (TimePeriod, PageHeader, DataTable). |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Ajout de l'import `Separator` manquant. |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Restauration du composant DashboardPage complet (Stats rapides). |
| `frontend/src/components/dashboard/APIStatusCards.tsx` | Modification | Recréation de `EmptyConnectors` et fix du type `SourceStatus`. |

#### Décisions techniques

1. **Build Integrity** : Passage au build Next.js en production pour valider l'absence d'erreurs TypeScript/Lint avant livraison.
2. **UI Resilience** : Reconstruction des fichiers tronqués lors des itérations précédentes pour garantir une interface fonctionnelle sans placeholders.
3. **Hyphen Consistency** : Harmonisation des noms de paquets système dans le Dockerfile backend.

#### ✅ Phase 5 (Hardening) — Tâches complétées
- [x] Stabilisation totale du build Docker Full Stack.
- [x] Résolution des erreurs de compilation Next.js.

---

### Itération 16 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Finalisation totale du Backend : Rapports globaux, Sécurité Profil et Sources Custom.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/routers/reports.py` | Modification | Implémentation de la fusion réelle de scans pour les rapports globaux. |
| `backend/app/routers/settings.py` | Modification | Endpoint de test pour les sources RSS/Atom avec aperçu d'items. |
| `frontend/src/app/(dashboard)/admin/settings/client.tsx` | Modification | Intégration complète du CRUD et des tests pour les sources custom. |
| `frontend/src/app/(dashboard)/profile/page.tsx` | Modification | Branchement des actions de changement de mot de passe et enrôlement MFA. |
| `frontend/src/lib/api.ts` | Modification | Ajout des fonctions `passwordChange`, `mfaSetup` et `mfaConfirm`. |

#### Décisions techniques

1. **Fusion de Scans** : La génération globale relit les fichiers JSON physiques des scans précédents pour garantir l'intégrité des findings agrégés sans surcharger la base de données.
2. **Validation Flux** : Utilisation de `feedparser` côté backend pour valider l'URL d'un flux RSS avant de permettre son enregistrement par l'admin.
3. **Sécurité UI** : Les dialogues de changement de mot de passe et MFA intègrent des validations de correspondance et des retours d'état clairs.

#### ✅ Phase 1.3, 2.2 & 4.2 — Tâches complétées
- [x] Phase 1.3 — Gestion complète des sources custom RSS.
- [x] Phase 2.2 — Sécurité Profil 100% fonctionnelle.
- [x] Phase 4.2 — Génération de rapports globaux consolidés.

---

### Itération 15
 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Finalisation de la génération de rapports PDF et des flux d'authentification MFA.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/routers/reports.py` | Création | Routeur pour la liste et l'export (PDF, HTML, JSON) des rapports. |
| `backend/app/report/engine.py` | Modification | Robustesse de WeasyPrint et gestion des fallbacks HTML. |
| `backend/app/engine/logic.py` | Modification | Activation de la génération PDF lors des scans. |
| `backend/Dockerfile` | Modification | Installation des dépendances système WeasyPrint (pango, cairo, etc.). |
| `backend/app/routers/auth.py` | Modification | Finalisation des endpoints `mfa/verify` et `mfa/confirm`. |
| `backend/app/engine/cve_monitor.py` | Modification | Implémentation du fetcher OSV.dev réel via `modified_id.csv`. |

#### Décisions techniques

1. **Isolation PDF** : WeasyPrint est installé comme dépendance optionnelle `[pdf]` mais activé par défaut dans le Dockerfile de production pour garantir l'export.
2. **Reconstruction Rapport** : L'endpoint d'export relit le JSON du scan pour reconstruire l'objet `FinalReport` et garantir une génération PDF identique à l'original.
3. **MFA State** : Utilisation du scan Redis pour retrouver le `user_id` associé à un `challenge_token` de manière sécurisée et sans état permanent.

#### ✅ Phase 2.2 & 4.1 — Tâches complétées
- [x] Phase 2.2 — Verification et confirmation MFA complètes.
- [x] Phase 4.1 — Export PDF fonctionnel et intégré.

---

### Itération 14
 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Implémentation d'un système global de Mock Data et finalisation des fondations backend.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/routers/dashboard.py` | Modification | Ajout de la logique de génération de données mockées dynamiques. |
| `backend/app/routers/cve.py` | Modification | Support des données de démo si aucune CVE réelle n'est présente. |
| `frontend/src/app/(dashboard)/admin/settings/client.tsx` | Modification | Ajout du switch "Données de démonstration" dans les paramètres avancés. |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Affichage de la bannière d'avertissement Mock globale. |
| `frontend/src/components/layout/ToolPageLayout.tsx` | Modification | Support du bandeau "Mode Démonstration" pour toutes les pages outils. |
| `frontend/src/components/dashboard/APIStatusCards.tsx` | Modification | Badge MOCK et statut Demo Mode pour les connecteurs. |
| `frontend/src/app/(dashboard)/tools/*/page.tsx` | Modification | Détection et transmission du statut isMock aux clients. |
| `frontend/src/lib/api.ts` | Modification | Ajout du flag `is_mock` aux interfaces `ConnectorStatus` et `DashboardStats`. |

#### Décisions techniques

1. **Mock On-the-fly** : Les données mockées ne sont pas stockées en base mais générées à la volée par l'API pour économiser les ressources et faciliter le switch oui/non.
2. **Visibilité MOCK** : Utilisation d'un code couleur orange et de badges explicites partout dans l'UI pour garantir que l'utilisateur sait quand il regarde de la donnée fictive.
3. **Persistance Settings** : Le mode Mock est persisté dans `SystemSettings` pour rester actif entre les sessions.

#### ✅ Phase 3.1 & Phase 5 (Hardening) — Tâches complétées
- [x] Phase 3.1 — Stockage Key-Value complet (Domaine, Maintenance, Mock Mode).
- [x] Système de Mock Data global (Backend + Frontend).

---

### Itération 13 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Mise en place des fondations Backend : Modèles SQLAlchemy, chiffrement Fernet et routeurs de paramètres.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `backend/app/models/cve.py` | Création | Modèles SQLAlchemy pour `CVEAlert` et `CustomFeedSource`. |
| `backend/app/models/settings.py` | Création | Modèle SQLAlchemy pour `SystemSettings` (Key-Value JSON). |
| `backend/app/core/config.py` | Modification | Ajout de `encryption_key` aux paramètres globaux. |
| `backend/app/core/security.py` | Modification | Implémentation du chiffrement/déchiffrement Fernet. |
| `backend/app/routers/api_keys.py` | Modification | Sécurisation des clés d'API via `encrypt_secret`. |
| `backend/app/routers/settings.py` | Création | Routeur pour la gestion des paramètres système et sources custom. |
| `backend/app/routers/cve.py` | Modification | Passage des mocks à la base de données réelle pour les alertes. |
| `backend/app/engine/cve_monitor.py` | Création | Début d'implémentation du moteur de collecte CVE (NVD, CVEFeed, GitHub). |
| `backend/app/main.py` | Modification | Enregistrement des nouveaux routeurs et correction des imports. |

#### Décisions techniques

1. **Security-First** : Implémentation immédiate du chiffrement Fernet pour éviter de stocker des clés API en clair dès les premières itérations backend.
2. **Key-Value Settings** : Utilisation d'une table flexible pour les paramètres système afin d'éviter des migrations DB à chaque ajout de configuration UI.
3. **Moteur CVE** : Structure asynchrone avec `CVEMonitor` gérant nativement le rate-limit strict du NVD.

#### ✅ Phase 1.2, 2.1 & 3.1 — Tâches complétées
- [x] Phase 1.2 — Modèles DB CVE & Custom Sources.
- [x] Phase 2.1 — Chiffrement Fernet des clés API.
- [x] Phase 3.1 — Modèle SystemSettings.

---

### Itération 12 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

**Objectif de l'itération** : Implémentation des pages manquantes (CVE, Profil, Changelog) et finalisation des paramètres d'instance. Création du plan de route pour le Backend.

#### ✅ Phase 6, 7 & 9 — Tâches complétées
- [x] Phase 9.1 à 9.5 — Page `/alerts/cve` complète.
- [x] Phase 7.2 — Page profil utilisateur (`/profile`).
- [x] Phase 6.1 — Page changelog (`/changelog`).
- [x] Phase 10.6 — Onglet "Sources custom" ajouté aux settings.

---

## 🤖 Prochain Agent — Reprendre ici

**Arrêté à** : Fondations backend en place (Modèles, Sécurité, Routeurs). Moteur CVE initialisé.
**Commit** : `HEAD`
**Ce qui reste (Priorité Backend)** :
- [ ] Finaliser `CVEMonitor` (implémenter OSV.dev et polling réel).
- [ ] Connecter la page Profil aux actions réelles (Change Password, Toggle MFA).
- [ ] Implémenter le stockage et le test des "Sources Custom" (RSS/Atom).
- [ ] Finaliser l'export PDF réel et la génération de rapports globaux.

**Points de vigilance** :
- Respecter les rate-limits NVD (5 req/30s).
- Utiliser `feedparser` pour les sources custom (attention aux injections XSS).
- Bien migrer les secrets du `.env` vers la DB de manière sécurisée.
