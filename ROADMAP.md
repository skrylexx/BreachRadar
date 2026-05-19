# ROADMAP — BreachRadar

> Journal de bord structuré — mis à jour à chaque itération IA ou humaine.
> **Protocole handoff** : Lire ce fichier + README.md avant toute contribution.

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
