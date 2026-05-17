# TODO — Développement Backend BreachRadar

> Branche de travail : `feat/backend-implementation`
> Référence : `Cahier-Des-Charges_BreachRadar.md`, `ROADMAP.md`
> Stack : FastAPI · SQLAlchemy (Async) · PostgreSQL · Redis · APScheduler

---

## État actuel

Le frontend est **100% opérationnel** et utilise actuellement des données factices (Mocks) pour certaines routes (CVE, Settings). L'objectif est maintenant de relier ces interfaces au moteur backend réel, d'implémenter la logique de scraping manquante, et d'assurer le chiffrement des données sensibles.

---

## PHASE 1 — Moteur CVE & Sources Custom (Priorité Haute)

> Remplacer les mocks dans `routers/cve.py` par des données réelles.

- [x] **1.1 — Moteur de collecte CVE (`engine/cve_monitor.py`)**
  - [x] Implémenter le fetcher **NVD API 2.0** : gestion du rate-limit (5 req/30s sans clé, 50 req/30s avec clé `CVE_NVD_API_KEY`).
  - [x] Implémenter le fetcher **OSV.dev** : filtrage par écosystème (npm, PyPI, Go, etc.).
  - [x] Implémenter le fetcher **GitHub Advisories** : parsing du flux Atom.
  - [x] Implémenter le fetcher **CVEFeed.io** : parsing des flux RSS (Critical, High).

- [x] **1.2 — Modèles & Stockage DB**
  - [x] Créer la table `CVEAlert` pour stocker les alertes en cache et éviter de spammer les API.
  - [x] Créer la table `CustomFeedSource` (id, name, url, category, enabled, last_polled_at, last_item_count).

- [x] **1.3 — Sources Custom (RSS/Atom)**
  - [x] Implémenter la lecture des flux personnalisés avec la librairie `feedparser`.
  - [x] Normaliser les entrées (titre, description sécurisée contre XSS, lien, date, sévérité déduite).
  - [x] Implémenter l'endpoint `/api/v1/settings/custom-sources/test` (fetch + aperçu 3 items).

- [x] **1.4 — Intégration Routeur & Scheduler**
  - [x] Connecter `routers/cve.py` à la base de données.
  - [x] Ajouter un job dans `scheduler.py` pour lancer le polling CVE toutes les X minutes (selon les settings).


---

## PHASE 2 — Chiffrement & Sécurité (Hardening)

> Assurer la sécurité des clés d'API et finaliser les flux d'authentification.

- [x] **2.1 — Chiffrement des clés API**
  - [x] Utiliser `cryptography.fernet` pour chiffrer la colonne `encrypted_value` dans le modèle `ApiKey`.
  - [x] Au démarrage du backend (lifespan), injecter les clés déchiffrées dans `app.core.config.settings` en donnant la priorité aux variables `.env`.

- [x] **2.2 — Finalisation MFA & Profil**
  - [x] Implémenter la logique complète de vérification dans `POST /auth/mfa/verify` (utiliser le `challenge_token` et Redis).
  - [x] Implémenter `POST /auth/me/change-password` pour la page Profil.
  - [x] Implémenter `POST /auth/me/toggle-mfa` (génération du secret TOTP, renvoi de l'URI otpauth pour QR Code).

- [x] **2.3 — Audit Trail Complet**
  - [x] S'assurer que les actions sensibles (connexion, erreur de connexion, modification de clé API, lancement de scan, suppression) sont enregistrées dans la table `AuditLog` via un middleware ou des dépendances.

---

## PHASE 3 — Paramètres Dynamiques (Settings)

> Remplacer les configurations en dur par des paramètres modifiables depuis la WebUI.

- [x] **3.1 — Stockage Key-Value**
  - [x] Créer une table `SystemSettings` (key, value JSON, updated_at).
  - [x] Stocker `TARGET_DOMAIN`, `maintenance_mode`, `default_language`, `cve_polling_interval`, `mock_data_enabled`.

- [x] **3.2 — Configuration SMTP & Notifications**
  - [x] Mettre à jour `routers/settings.py` (ou `admin/smtp.py`) pour sauvegarder les infos SMTP chiffrées en base.
  - [x] Implémenter l'endpoint de test SMTP (envoyer un mail factice pour vérifier la connexion).
  - [x] Lier les alertes CVE critiques (`notifications/engine.py`) au moteur d'envoi d'email.

---

## PHASE 4 — Rapports & Exports PDF

> Fournir les livrables attendus par les utilisateurs.

- [x] **4.1 — Connecter l'Export PDF**
  - [x] Lier `GET /api/v1/reports/{id}/export?format=pdf` à la fonction `_generate_pdf()` de `report/engine.py`.
  - [x] Configurer WeasyPrint avec les dépendances système dans le Dockerfile.

- [x] **4.2 — Génération de Rapport Global**
  - [x] Implémenter `POST /api/v1/reports/generate` : agréger les résultats de multiples `ScanResult` sur une période de temps donnée (start_date, end_date) en un seul document consolidé.

---

## PHASE 5 — Validation & Tests OSINT

> S'assurer que les connecteurs externes fonctionnent parfaitement.

- [x] **5.1 — Vérification des connecteurs**
  - [x] Corriger le build des images Docker (Backend & Frontend).
  - [x] Résoudre les erreurs de typage et les composants manquants dans la WebUI.
  - [x] S'assurer que les limites de rate-limit sont bien respectées par `hibp.py` (1.5s entre chaque requête).
  - [x] Vérifier que `intelx.py`, `dehashed.py`, `leakcheck.py` gèrent correctement les exceptions réseaux (timeout, erreur 500, quotas atteints).

- [/] **5.2 — Tests Unitaires**
  - [x] Vérifier la réussite du build Next.js en production (CI/CD check).
  - [x] Écrire des tests asynchrones (pytest + httpx) pour `cve_monitor.py` avec des mocks.
  - [ ] Vérifier la logique de `RansomwareTracker` (une alerte ransomware doit forcer la sévérité globale à CRITICAL).

- [x] **5.3 — Audit Automatisé**
  - [x] Lancer `bandit -r backend/app` pour vérifier les failles courantes.
  - [x] Exécuter `semgrep` pour détecter d'éventuelles vulnérabilités (ex: injections SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
ons SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
*
ons SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
