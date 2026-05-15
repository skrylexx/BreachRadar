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
Phase 5 — Hardening   [█░░░░░░░░░]  10%

── Frontend (TODO.md) ──────────────────
Phase 0 — Fondations  [██████████] 100%
Phase 1 — Dashboard   [██████████] 100%
Phase 2 — Tools       [██████████] 100%
Phase 3 — Reports     [██████████] 100%
Phase 4 — Ransomware  [██████████] 100%
Phase 5 — Admin       [██████████] 100%

── Backend Implementation ──────────────
Phase 1 — CVE Engine  [████████░░]  80%
Phase 2 — Security    [██████░░░░]  60%
Phase 3 — Settings    [████████░░]  80%
Phase 4 — Reports     [█████░░░░░]  50%
```

---

## Vision globale

### Phase 4 — WebUI Gouvernance SOC (100%)
- [x] Infrastructure Docker WebUI
- [x] Backend FastAPI : JWT, RBAC Admin/Viewer, TOTP MFA
- [x] Frontend Next.js : thème SOC, sidebar fine, radar animation
- [x] Pages : `/scans`, `/api-keys`, `/users`, `/changelog`, `/alerts/cve`, `/profile`
- [x] Intégration next-intl
- [x] Export PDF fonctionnel avec WeasyPrint

---

## CHANGELOG

### Itération 15 — 2026-05-15 (Gemini 2.0 Flash — Antigravity)

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
