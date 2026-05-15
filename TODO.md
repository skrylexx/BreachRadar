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

- [ ] **1.1 — Moteur de collecte CVE (`engine/cve_monitor.py`)**
  - Implémenter le fetcher **NVD API 2.0** : gestion du rate-limit (5 req/30s sans clé, 50 req/30s avec clé `CVE_NVD_API_KEY`).
  - Implémenter le fetcher **OSV.dev** : filtrage par écosystème (npm, PyPI, Go, etc.).
  - Implémenter le fetcher **GitHub Advisories** : parsing du flux Atom.
  - Implémenter le fetcher **CVEFeed.io** : parsing des flux RSS (Critical, High).

- [ ] **1.2 — Modèles & Stockage DB**
  - Créer la table `CVEAlert` pour stocker les alertes en cache et éviter de spammer les API.
  - Créer la table `CustomFeedSource` (id, name, url, category, enabled, last_polled_at, last_item_count).

- [ ] **1.3 — Sources Custom (RSS/Atom)**
  - Implémenter la lecture des flux personnalisés avec la librairie `feedparser`.
  - Normaliser les entrées (titre, description sécurisée contre XSS, lien, date, sévérité déduite).
  - Implémenter l'endpoint `/api/v1/settings/custom-sources/test` (fetch + aperçu 3 items).

- [ ] **1.4 — Intégration Routeur & Scheduler**
  - Connecter `routers/cve.py` à la base de données.
  - Ajouter un job dans `scheduler.py` pour lancer le polling CVE toutes les X minutes (selon les settings).

---

## PHASE 2 — Chiffrement & Sécurité (Hardening)

> Assurer la sécurité des clés d'API et finaliser les flux d'authentification.

- [ ] **2.1 — Chiffrement des clés API**
  - [x] Utiliser `cryptography.fernet` pour chiffrer la colonne `encrypted_value`.
  - [ ] Au démarrage du backend (lifespan), injecter les clés déchiffrées.

- [ ] **2.2 — Finalisation MFA & Profil**
  - Implémenter la logique complète de vérification dans `POST /auth/mfa/verify` (utiliser le `challenge_token` et Redis).
  - Implémenter `POST /auth/me/change-password` pour la page Profil.
  - Implémenter `POST /auth/me/toggle-mfa` (génération du secret TOTP, renvoi de l'URI otpauth pour QR Code).

- [ ] **2.3 — Audit Trail Complet**
  - S'assurer que les actions sensibles (connexion, erreur de connexion, modification de clé API, lancement de scan, suppression) sont enregistrées dans la table `AuditLog` via un middleware ou des dépendances.

---

## PHASE 3 — Paramètres Dynamiques (Settings)

> Remplacer les configurations en dur par des paramètres modifiables depuis la WebUI.

- [x] **3.1 — Stockage Key-Value**
  - [x] Créer une table `SystemSettings` (key, value JSON, updated_at).
  - [x] Stocker `TARGET_DOMAIN`, `maintenance_mode`, `default_language`, `cve_polling_interval`, `mock_data_enabled`.

- [ ] **3.2 — Configuration SMTP & Notifications**

  - Mettre à jour `routers/settings.py` (ou `admin/smtp.py`) pour sauvegarder les infos SMTP chiffrées en base.
  - Implémenter l'endpoint de test SMTP (envoyer un mail factice pour vérifier la connexion).
  - Lier les alertes CVE critiques (`notifications/engine.py`) au moteur d'envoi d'email.

---

## PHASE 4 — Rapports & Exports PDF

> Fournir les livrables attendus par les utilisateurs.

- [x] **4.1 — Connecter l'Export PDF**
  - [x] Lier `GET /api/v1/reports/{id}/export?format=pdf` à la fonction `_generate_pdf()` de `report/engine.py`.
  - [x] Configurer WeasyPrint avec les dépendances système dans le Dockerfile.

- [ ] **4.2 — Génération de Rapport Global**
  - Implémenter `POST /api/v1/reports/generate` : agréger les résultats de multiples `ScanResult` sur une période de temps donnée (start_date, end_date) en un seul document consolidé.

---

## PHASE 5 — Validation & Tests OSINT

> S'assurer que les connecteurs externes fonctionnent parfaitement.

- [ ] **5.1 — Vérification des connecteurs**
  - S'assurer que les limites de rate-limit sont bien respectées par `hibp.py` (1.5s entre chaque requête).
  - Vérifier que `intelx.py`, `dehashed.py`, `leakcheck.py` gèrent correctement les exceptions réseaux (timeout, erreur 500, quotas atteints).

- [ ] **5.2 — Tests Unitaires**
  - Écrire des tests asynchrones (pytest + httpx) pour `cve_monitor.py` avec des mocks.
  - Vérifier la logique de `RansomwareTracker` (une alerte ransomware doit forcer la sévérité globale à CRITICAL).

- [ ] **5.3 — Audit Automatisé**
  - Lancer `bandit -r backend/app` pour vérifier les failles courantes.
  - Exécuter `semgrep` pour détecter d'éventuelles vulnérabilités (ex: injections SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
ons SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
*
ons SQL via SQLAlchemy, mauvaise gestion des secrets).

---
*Dernière mise à jour : 2026-05-15*
