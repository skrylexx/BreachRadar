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
Phase 5 — Hardening   [░░░░░░░░░░]   0%

── Frontend (TODO.md) ──────────────────
Phase 0 — Fondations  [██████████] 100%
Phase 1 — Dashboard   [██░░░░░░░░]  20%  (structure OK, mock data)
Phase 2 — Tools       [░░░░░░░░░░]   0%
Phase 3 — Reports     [░░░░░░░░░░]   0%
Phase 4 — Ransomware  [░░░░░░░░░░]   0%
Phase 5 — Admin       [░░░░░░░░░░]   0%
```

---

## Vision globale

### Phase 1 — MVP (en cours)
**Objectif** : Infrastructure de base fonctionnelle, sources gratuites prioritaires, rapport complet avec section ransomware.

- [x] README.md et ROADMAP.md
- [x] pyproject.toml (dépendances)
- [x] .env.example (template configuration)
- [x] .gitignore
- [x] docker-compose.yml (BreachRadar + RansomLook stack complète)
- [x] Dockerfile
- [x] Makefile
- [x] breachradar/models/finding.py (LeakFinding, Severity)
- [x] breachradar/models/ransom.py (RansomFinding, RansomStats, RansomStatus)
- [x] breachradar/models/report.py (FinalReport, ReportMetadata)
- [x] breachradar/config/settings.py (Pydantic Settings)
- [x] breachradar/config/sources.yaml
- [x] breachradar/config/group_names.yaml
- [x] breachradar/clients/base.py (BaseLeakClient ABC)
- [x] breachradar/clients/ransomlook.py (RansomLookClient)
- [x] breachradar/core/sanitizer.py (DataSanitizer)
- [x] breachradar/core/aggregator.py (ResultAggregator)
- [x] breachradar/core/ransom_tracker.py (RansomwareTracker)
- [x] breachradar/config/source_registry.py (SourceRegistry — disponibilité dynamique)
- [x] SECURITY.md (procédures sécurité complètes)
- [x] .pre-commit-config.yaml (detect-secrets, ruff, hooks git)
- [x] scripts/verify_sanitizer.py (vérification manuelle sanitizer)
- [x] tests/test_source_registry.py (14 tests de disponibilité des sources)
- [x] breachradar/clients/hibp.py
- [x] breachradar/clients/github_monitor.py
- [x] breachradar/core/orchestrator.py
- [x] breachradar/core/scheduler.py
- [x] breachradar/resolver/email_resolver.py
- [x] breachradar/report/engine.py
- [x] breachradar/report/templates/report.md.j2
- [x] breachradar/report/templates/report.html.j2
- [x] breachradar/report/templates/notification.txt.j2
- [x] breachradar/notifications/engine.py
- [x] breachradar/main.py (CLI Typer)
- [x] tests/conftest.py
- [x] tests/test_sanitizer.py
- [x] tests/test_aggregator.py
- [x] tests/test_ransom_tracker.py
- [x] tests/test_security.py
- [x] tests/test_clients/test_hibp.py
- [x] tests/test_clients/test_ransomlook.py
- [x] tests/fixtures/ransomlook/victim_found.json
- [x] tests/fixtures/ransomlook/victim_not_found.json

### Phase 2 — Enrichissement sources
- [x] breachradar/clients/leakcheck.py
- [x] breachradar/clients/dehashed.py
- [x] breachradar/clients/pastebin_monitor.py
- [x] Domain Email Resolver (Hunter.io + theHarvester)
- [x] Rapport HTML avec dashboard visuel
- [x] Scheduler + notifications email

### Phase 3 — Monitoring continu
- [x] breachradar/clients/telegram_monitor.py
- [x] GitHub webhook monitoring
- [x] breachradar/clients/intelx.py
- [x] Docker full stack (un seul `docker compose up`)
- [x] Export PDF

### Phase 4 — WebUI Gouvernance SOC (100%)
- [x] Infrastructure Docker WebUI (`--profile ui`) — 4 services ajoutés
- [x] Backend FastAPI : JWT, RBAC Admin/Viewer, TOTP MFA, models, routers
- [x] Frontend Next.js : thème #09090b, sidebar fine, radar animation
- [x] Composants Dashboard : RiskHeatmap, APIStatusCards, FindingsTable
- [x] Documentation : README.md + ROADMAP.md + webui/.env.example
- [x] Migration totale vers WebUI (Suppression du CLI)
- [ ] Pages restantes : `/scans`, `/api-keys`, `/users`, `/changelog`
- [ ] MFA verify endpoint complet
- [ ] Intégration next-intl + tests E2E
- [ ] Export PDF + config SMTP depuis UI

### Phase 5 — Hardening
- [ ] Audit sécurité (bandit, semgrep)
- [ ] Rotation automatique des clés API
- [ ] Chiffrement des clés API stockées (Fernet)
- [ ] Documentation mkdocs
- [ ] Alertes PagerDuty / OpsGenie

---

## CHANGELOG

### Itération 9 — 2026-05-11 (Claude Sonnet 4.6 — Antigravity)

**Objectif de l'itération** : Implémentation de la Phase 0 (Fondations & Infrastructure UI) du TODO.md frontend.

#### Fichiers créés/modifiés

| Fichier | Nature | Description |
|---|---|---|
| `frontend/src/app/globals.css` | Modification | Restauration du design system BreachRadar (tokens HSL, variables de sévérité `--color-critical/high/medium/low`, utilitaires custom) |
| `frontend/src/components/ui/severity-badge.tsx` | Création | `<SeverityBadge>` — badge coloré CRITICAL/HIGH/MEDIUM/LOW/NONE/INFO réutilisable |
| `frontend/src/components/ui/status-dot.tsx` | Création | `<StatusDot>` — indicateur de statut source avec animation ping (ok/warning/error/unknown) |
| `frontend/src/components/ui/page-header.tsx` | Création | `<PageHeader>` — en-tête de page standard avec breadcrumb et slot actions |
| `frontend/src/components/ui/empty-state.tsx` | Création | `<EmptyState>` — état vide standard avec icône radar, message et CTA |
| `frontend/src/components/ui/time-filter.tsx` | Création | `<TimeFilter>` — sélecteur 7j/1m/6m/12m/Tout |
| `frontend/src/components/ui/radar-spinner.tsx` | Création | `<RadarSpinner>` — spinner SVG animé type radar (pas de dépendance) |
| `frontend/src/components/ui/data-table.tsx` | Création | `<DataTable>` — tableau paginé réutilisable avec tri, pagination client/serveur, loading, empty state |
| `frontend/src/lib/api.ts` | Réécriture | Client HTTP enrichi : types métier complets + fonctions typées par domaine (dashboardApi, scansApi, findingsApi, reportsApi, ransomwareApi, cveApi, usersApi, apiKeysApi, auditApi, authApi) |
| `frontend/src/middleware.ts` | Création | Middleware Next.js Edge : guard JWT cookie + RBAC admin (redirect /login ou /403) |
| `frontend/src/app/403/page.tsx` | Création | Page 403 custom — cohérente avec le thème SOC |
| `frontend/src/app/not-found.tsx` | Création | Page 404 custom — cohérente avec le thème SOC |
| `frontend/src/components/layout/Sidebar.tsx` | Réécriture | Sidebar étendue avec toutes les routes du TODO (Tools, Alerts, Admin collapsible) |
| `frontend/src/components/layout/Header.tsx` | Modification | Intégration de next-intl et ajout du sélecteur de langue dynamique (FR/EN) |
| `frontend/src/components/dashboard/RansomwareAlertBlock.tsx` | Création | Bloc d'alerte Ransomware dynamique |
| `frontend/src/components/dashboard/CVEAlertsBlock.tsx` | Création | Bloc des dernières alertes CVE et exploits |
| `frontend/src/components/dashboard/ScansTableBlock.tsx` | Création | Tableau des derniers scans |
| `frontend/src/components/dashboard/QuickAccessBlock.tsx` | Création | Bloc d'accès rapide aux outils |
| `frontend/src/app/(dashboard)/scans/page.tsx` | Création | Page des scans avec historique et bouton de lancement |
| `frontend/src/app/(dashboard)/scans/client.tsx` | Création | Client des scans avec DataTable |
| `frontend/src/components/layout/ToolPageLayout.tsx` | Création | Layout réutilisable pour toutes les pages outils |
| `frontend/src/app/(dashboard)/tools/hibp/*` | Création | Page outil HIBP (Server + Client) |
| `frontend/src/app/(dashboard)/tools/github/*` | Création | Page outil GitHub (Server + Client) |
| `frontend/src/app/(dashboard)/tools/ransomlook/*` | Création | Page outil RansomLook (Server + Client) |
| `frontend/src/app/(dashboard)/tools/leakcheck/*` | Création | Page outil LeakCheck (Server + Client) |
| `frontend/src/app/(dashboard)/tools/urlscan/*` | Création | Page outil URLScan (Server + Client) |
| `frontend/src/components/ui/badge.tsx` + 14 autres | Création | Composants Shadcn/UI installés : badge, table, tabs, select, dialog, skeleton, tooltip, switch, form, input, label, separator, dropdown-menu, alert, progress |
| `frontend/src/app/(dashboard)/page.tsx` | Modification | Câblage complet de la page avec l'API Backend via `searchParams` pour les filtres temporels |

#### Décisions techniques

1. **Design system** : Shadcn init a écrasé les tokens oklch génériques — restaurés en HSL conformément au CDC (`#09090b`, `#18181b`, `#38bdf8`).
2. **DataTable** : Implémentation vanilla (sans Tanstack Table) pour minimiser les dépendances — upgrade possible si nécessaire.
3. **Middleware** : Décode JWT basique côté Edge (sans crypto) pour UX guard — la vérification de signature réelle reste côté FastAPI.
4. **Sidebar** : Section Admin collapsible (état local React) pour ne pas surcharger la sidebar 56px.
5. **API client** : Toutes les fonctions sont typées avec les interfaces métier BreachRadar — prêtes pour les pages Phase 1-10.

#### ✅ Phase 0 — Tâches complétées
- [x] 0.1 — Design system tokens (globals.css, variables sévérité, polices)
- [x] 0.2 — Composants Shadcn/UI installés (15 composants)
- [x] 0.3 — Composants partagés custom (SeverityBadge, StatusDot, PageHeader, EmptyState, DataTable, RadarSpinner, TimeFilter)
- [x] 0.4 — i18n setup (`next-intl` via configuration non-routable pour préserver les URLs du dashboard, `messages/en.json`, `messages/fr.json`)
- [x] 0.5 — Couche API client enrichie (fonctions typées par domaine)
- [x] 0.6 — Guard authentification (middleware.ts JWT + RBAC)
- [~] 0.7 — Dark/Light mode toggle dans le Header (Annulé : le contexte SOC impose un thème Dark obligatoire global, aucune gestion de mode clair n'est autorisée).
- [x] 7.4 — Pages 403 / 404 custom

#### ✅ Phase 1 — Dashboard principal
- [x] 1.1 — Graphique d'évolution global (`RiskHeatmap` + `TimeFilter` fonctionnel modifiant les `searchParams`)
- [x] 1.2 — Cards connecteurs / sources (`APIStatusCards` + statut dynamique)
- [x] 1.3 — Bloc alerte RansomLook conditionnel
- [x] 1.4 — Dernières CVE & Exploits (composant `CVEAlertsBlock`)
- [x] 1.5 — Dernières alertes "Findings" (refonte avec la `DataTable` générique)

#### ✅ Phase 2 — Liste et Scans
- [x] Page `/scans` — Liste paginée de l'historique des scans avec possibilité de relancer un scan via l'API.

#### ✅ Phase 2 — Pages par Outil
- [x] Phase 2.1 — Layout partagé `ToolPageLayout`
- [x] Phase 2.2 à 2.6 — Pages spécifiques (HIBP, GitHub, RansomLook, LeakCheck, URLScan)

#### ⏳ Prochaine session — Phase 3 (Rapports)
- [ ] Phase 3.1 — Liste des rapports
- [ ] Phase 3.2 — Export PDF

---

### Itération 8 — 2026-05-04 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Migration totale de l'architecture "CLI + WebUI" vers "WebUI 100%". Suppression du mode CLI Typer.

#### Fichiers créés/modifiés
- Restructuration totale de l'arborescence : `webui/backend` -> `backend`, `webui/frontend` -> `frontend`.
- Déplacement de `breachradar/` au sein de `backend/app/engine/`, `clients/`, `report/`, `notifications/`, `resolver/`.
- Suppression de `breachradar/main.py`.
- Mise à jour majeure du `docker-compose.yml` (suppression profil `ui`, la WebUI démarre par défaut).
- `backend/pyproject.toml` : fusion de `requirements.txt` et `pyproject.toml` via `uv`.
- `.env.example` : unifié et centralisé.
- `backend/app/main.py` : intégration d'APScheduler dans le cycle de vie FastAPI (`lifespan`).
- Refonte totale du `README.md` et `QUICKSTART.md` pour refléter l'utilisation exclusive de l'interface Web.

#### Décisions techniques
- L'orchestrateur, le scheduler et la réception des webhooks GitHub (précédemment sur `aiohttp`) font désormais intégralement partie de l'application FastAPI centrale.
- Simplification du déploiement : tout démarre avec un unique `docker compose up -d`.

### Itération 7 — 2026-05-04 (Claude Sonnet 4.6 — Antigravity)

**Objectif de l'itération** : Initialisation de la WebUI BreachRadar — Phase 4 (Gouvernance SOC).

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `docker-compose.yml` | Ajout profil `ui` : 4 services (postgres, redis, api, frontend) |
| `webui/.env.example` | Variables d'env dédiées WebUI |
| `webui/backend/Dockerfile` | Image Python 3.12-slim non-root |
| `webui/backend/requirements.txt` | FastAPI, SQLAlchemy, pyotp, slowapi, etc. |
| `webui/backend/app/main.py` | Application FastAPI + CORS + TrustedHost + rate limiting |
| `webui/backend/app/core/config.py` | Pydantic Settings — validation JWT, passwords, SMTP |
| `webui/backend/app/core/security.py` | JWT (access 15min + refresh 7j) + bcrypt + TOTP |
| `webui/backend/app/core/database.py` | SQLAlchemy async engine PostgreSQL |
| `webui/backend/app/core/redis.py` | Blacklist tokens + challenges MFA temporaires |
| `webui/backend/app/core/init_db.py` | Création admin initial au premier boot |
| `webui/backend/app/models/user.py` | Modèle User (RBAC, MFA, rotation MDP) |
| `webui/backend/app/models/scan.py` | Modèle ScanResult (RGPD — stats agrégées uniquement) |
| `webui/backend/app/models/api_key.py` | Modèle APIKey (chiffrement à implémenter) |
| `webui/backend/app/models/audit_log.py` | Journal d'audit (traçabilité RGPD) |
| `webui/backend/app/schemas/auth.py` | Schémas Pydantic auth (login, MFA, password) |
| `webui/backend/app/schemas/user.py` | Schémas Pydantic user (CRUD) |
| `webui/backend/app/schemas/scan.py` | Schémas Pydantic scan (stats, trigger) |
| `webui/backend/app/routers/auth.py` | Login/logout/MFA/password + audit logs |
| `webui/backend/app/routers/users.py` | CRUD utilisateurs (admin uniquement) |
| `webui/backend/app/routers/scans.py` | Liste + stats + déclenchement manuel |
| `webui/backend/app/routers/api_keys.py` | Gestion clés API connecteurs |
| `webui/backend/app/dependencies/auth.py` | RBAC : CurrentUser, AdminUser, ViewerUser |
| `webui/frontend/Dockerfile` | Multi-stage build Node.js 20 non-root |
| `webui/frontend/next.config.ts` | Proxy API, security headers, standalone output |
| `webui/frontend/package.json` | Next.js 15, Radix UI, Recharts, next-intl |
| `webui/frontend/tailwind.config.ts` | Design system complet + animations radar |
| `webui/frontend/src/app/globals.css` | Thème dark #09090b, badges sévérité, scrollbar |
| `webui/frontend/src/app/layout.tsx` | Root layout Inter + JetBrains Mono |
| `webui/frontend/src/app/(auth)/login/page.tsx` | Login + animation radar SVG en fond |
| `webui/frontend/src/app/(dashboard)/layout.tsx` | Layout sidebar + header |
| `webui/frontend/src/app/(dashboard)/page.tsx` | Dashboard : stats, heatmap, API cards, findings |
| `webui/frontend/src/components/layout/Sidebar.tsx` | Sidebar fine icônes + tooltips + indicator actif |
| `webui/frontend/src/components/layout/Header.tsx` | Header + sélecteur langue + user menu |
| `webui/frontend/src/components/dashboard/RadarLoader.tsx` | Animation SVG radar (scan + landing) |
| `webui/frontend/src/components/dashboard/RiskHeatmap.tsx` | Recharts BarChart empilé + sélecteur période |
| `webui/frontend/src/components/dashboard/APIStatusCards.tsx` | Cards statut connecteurs bordure colorée |
| `webui/frontend/src/components/dashboard/FindingsTable.tsx` | Tableau Stripe-style + badges sévérité |
| `webui/frontend/src/lib/api.ts` | Fetch wrapper HttpOnly cookies + redirects |
| `webui/frontend/src/lib/i18n.ts` | Dictionnaire EN/FR typé |
| `README.md` | Section WebUI complète |
| `ROADMAP.md` | Ce fichier — itération 7 |

#### Décisions techniques

1. **Profil Docker `--profile ui`** : Séparation stricte de la stack CLI existante. `docker compose up -d` reste inchangé — la WebUI s'ajoute avec `--profile ui`.
2. **JWT en HttpOnly Cookies** : Access token (15 min) + Refresh token (7 j, limité au path `/auth/refresh`). Protection XSS par design.
3. **TOTP MFA** : Implémenté via `pyotp`. Flow complet : generate secret → QR code base64 → verify. Le challenge MFA utilise Redis avec TTL 5 min (anti-replay).
4. **Politique MDP** : 16 chars (admin), 12 chars (viewer), rotation 180 jours sauf si >24 chars. Validation côté API.
5. **Audit Log** : Table dédiée avec `user_email`, `action`, `details` (JSONB), `ip_address`. Jamais de données sensibles dans les `details`.
6. **Design SOC** : Fond `#09090b`, surfaces `#18181b`, accent `#38bdf8`. Animations radar SVG natives (pas de librairie d'animation). Sidebar 56px icônes uniquement.
7. **Recharts** : BarChart empilé par sévérité (critique/high/medium/low) — code couleur cyber standard respecté.
8. **i18n** : Dictionnaire statique EN/FR typé TypeScript — `next-intl` Context Provider à intégrer en prochaine itération.

#### ⚠️ Points de vigilance pour la prochaine IA

1. **MFA Verify endpoint** : Le `challenge_token` doit encoder le `user_id` (JWT signé ou mapping Redis). L'endpoint `/auth/mfa/verify` est marqué `501 Not Implemented` — à compléter.
2. **Fernet encryption** : Les clés API sont actuellement stockées en clair dans `encrypted_key`. Implémenter le chiffrement Fernet en priorité.
3. **`npm install` à exécuter** : Le répertoire `webui/frontend` n'a pas de `node_modules`. Exécuter `npm install` depuis `webui/frontend/` avant le build Docker.
4. **Pages manquantes** : `/scans`, `/api-keys`, `/users`, `/changelog` — structures créées, contenu à implémenter.
5. **Route `/` → `/auth/login`** : Ajouter un middleware Next.js pour rediriger les non-authentifiés.

---

### Itération 1 — 2026-04-30 (Claude Sonnet — Antigravity)

**Objectif de l'itération** : Poser les bases solides de la Phase 1 — infrastructure, modèles, clients prioritaires, sécurité by design.

#### Fichiers créés

| Fichier | Description |
|---|---|
| `README.md` | Documentation complète : architecture, installation, usage, arborescence |
| `ROADMAP.md` | Ce fichier — journal de bord + changelog + suivi d'avancement |
| `pyproject.toml` | Dépendances complètes selon le cahier des charges (uv/poetry) |
| `.env.example` | Template de configuration — toutes les clés API documentées |
| `.gitignore` | Exclusions : .env, reports/, sessions Telegram, caches |
| `docker-compose.yml` | Stack complète : BreachRadar + RansomLook (app + redis + tor) |
| `Dockerfile` | Image Python 3.12-slim, non-root, uv optimisé |
| `Makefile` | Toutes les commandes du cahier des charges |
| `breachradar/__init__.py` | Package init avec version |
| `breachradar/models/finding.py` | LeakFinding, Severity, EmailFindingResult |
| `breachradar/models/ransom.py` | RansomFinding, RansomStats, RansomStatus |
| `breachradar/models/report.py` | FinalReport, ReportMetadata, SeverityBreakdown |
| `breachradar/config/settings.py` | Pydantic Settings — validation complète |
| `breachradar/config/sources.yaml` | Activation/désactivation de chaque source |
| `breachradar/config/group_names.yaml` | Mapping 40+ groupes ransomware |
| `breachradar/clients/base.py` | BaseLeakClient ABC — interface commune |
| `breachradar/clients/ransomlook.py` | RansomLookClient complet avec retry + dedup |
| `breachradar/core/sanitizer.py` | DataSanitizer — masquage données sensibles |
| `breachradar/core/aggregator.py` | ResultAggregator — dédup + sévérité |
| `breachradar/core/ransom_tracker.py` | RansomwareTracker — orchestration + alerte immédiate |
| `reports/.gitkeep` | Répertoire de sortie (gitignored) |

#### Décisions techniques prises

1. **uv** choisi comme package manager (plus rapide que pip/poetry, recommandé dans le CdC).
2. **RansomLookClient** intègre la déduplication par `(group_name, post_title, published)` pour éviter les doublons multi-termes.
3. **DataSanitizer** couvre 9 patterns sensibles : passwords, MD5/SHA-1/SHA-256/bcrypt, tokens API, base64.
4. **ResultAggregator** : un seul RansomFinding élève la sévérité GLOBALE à CRITICAL (règle métier du CdC).
5. **RansomwareTracker** : l'alerte immédiate est déclenchée AVANT la fin du scan complet (fenêtre de réaction critique).
6. **BaseLeakClient** : interface ABC avec `check_email` et `check_domain` + rate limiter intégré.

#### Prochaines tâches (priorité pour l'itération suivante)

1. **`breachradar/clients/hibp.py`** — Client HIBP avec k-anonymity pour les passwords + rate limit 1500ms
2. **`breachradar/clients/github_monitor.py`** — Recherche de credentials hardcodés dans les repos publics
3. **`breachradar/core/orchestrator.py`** — Chef d'orchestre : asyncio.gather() sur tous les clients
4. **`breachradar/main.py`** — CLI Typer avec les commandes : scan, ransomlook, check, schedule, sources
5. **`breachradar/report/engine.py`** — Générateur de rapports Jinja2 (MD + JSON)
6. **`tests/test_sanitizer.py`** + **`tests/test_ransom_tracker.py`** — Tests unitaires prioritaires

---

### Itération 3 — 2026-04-30 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Finalisation de la Phase 1 (MVP à 100%) en implémentant l'orchestrateur, le reporting complet et les clients manquants (HIBP, GitHub).

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `breachradar/clients/hibp.py` | Implémentation du client HIBP (Rate Limiting de 1.5s, support K-Anonymity pour MDP) |
| `breachradar/clients/github_monitor.py` | Recherche de mentions de domaines et d'emails sur GitHub (gestion d'API anonyme) |
| `breachradar/core/orchestrator.py` | Orchestration parallèle des clients avec `asyncio.gather` |
| `breachradar/core/scheduler.py` | Placeholder en prévision de la Phase 2 |
| `breachradar/resolver/email_resolver.py` | Résolveur initial (liste commune de préfixes et lecture fichier `emails.txt`) |
| `breachradar/report/engine.py` | Générateur de rapports exploitant Jinja2 pour Markdown/HTML et Pydantic pour le JSON |
| `breachradar/report/templates/report.*.j2` | 3 templates Jinja2 (Markdown, HTML, Texte/Notification) respectant la RGPD |
| `breachradar/notifications/engine.py` | Envoi d'alertes webhook pour les compromissions critiques RansomLook |
| `breachradar/main.py` | Interface ligne de commande basée sur `typer` (`scan`, `check`, `ransomlook`, `sources`, etc.) |
| `tests/test_clients/test_*.py` | Tests unitaires pour les clients HIBP et RansomLook |

#### Décisions techniques prises

1. **Typer CLI** : Adopté pour fournir une interface élégante et robuste dans `main.py` en exploitant `asyncio.run()`.
2. **Templating Jinja2** : Les rapports Markdown et HTML partagent un filtre `mask_onion` garantissant qu'aucune URL `.onion` brute ne soit insérée dans le rendu final.
3. **Rate Limiting** : `HIBPClient` intègre un délai explicite de 1.5 seconde avant requête et `GitHubClient` de 2.0 secondes. L'orchestrateur lance les scans sur une liste d'emails en traitant par lots sans bloquer la boucle asynchrone globale.
4. **Email Resolver** : Une base simple en phase 1 pour tester rapidement, avant l'arrivée de theHarvester en phase 2.

#### Prochaines tâches (Phase 2 et début Phase 3)
1. Implémenter le client `pastebin_monitor.py` pour clôturer l'enrichissement des sources.
2. Rapport HTML avec dashboard visuel (améliorer `report.html.j2`).
3. Démarrer la Phase 3 : Telegram Monitor, GitHub webhook, IntelX, Docker full stack.

---

### Itération 4 — 2026-04-30 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Exécution de la Phase 2. Implémentation des clients payants, résolution d'emails avancée avec outils OSINT, et mise en place d'un véritable Scheduler avec APScheduler.

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `breachradar/clients/leakcheck.py` | Implémentation du client LeakCheck API v2. |
| `breachradar/clients/dehashed.py` | Implémentation du client Dehashed API. |
| `breachradar/core/orchestrator.py` | Intégration des clients LeakCheck et Dehashed au moment de l'initialisation. |
| `breachradar/config/settings.py` | Ajout de `hunter_api_key` pour configurer le résolveur d'emails. |
| `breachradar/resolver/email_resolver.py` | Intégration de Hunter.io (API) et de theHarvester (via `subprocess`). |
| `breachradar/core/scheduler.py` | Implémentation de `ScanScheduler` utilisant `APScheduler` (CronTrigger). |
| `breachradar/main.py` | Mise à jour de la commande `schedule` pour utiliser `ScanScheduler` de façon non bloquante. |
| `tests/test_aggregator.py` | Création de la suite de tests (déduplication, sévérité, priorisation RansomLook). |
| `tests/test_orchestrator.py` | Création de la suite de tests pour l'orchestrateur (tests async avec mocks). |

#### Décisions techniques prises

1. **Email Resolver** : Maintien du comportement non bloquant. TheHarvester est exécuté via `asyncio.create_subprocess_exec` et analysé à la volée.
2. **Scheduler** : `APScheduler` (via `AsyncIOScheduler`) a été intégré, utilisant la syntaxe cron définie dans la configuration `.env`. L'event loop est gérée proprement dans `main.py`.

#### Prochaines tâches (Phase 3)

1. Démarrer la Phase 3 : Monitoring continu (Telegram, Webhook GitHub, IntelX).
2. Construire la stack Docker complète (`docker-compose.yml` avec `entrypoint.sh`).
3. Ajouter l'export PDF (Weasyprint).

---

### Itération 5 — 2026-04-30 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Clôture de la Phase 2. Réalisation d'un Dashboard HTML visuel premium, création du client Pastebin OSINT, et configuration de l'envoi d'emails SMTP pour les alertes critiques.

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `breachradar/report/templates/report.html.j2` | Refonte complète : UI/UX Premium, Glassmorphism, Dark Mode, Grilles CSS. |
| `breachradar/clients/pastebin_monitor.py` | Client OSINT via l'API publique de PsbDmp.ws. |
| `breachradar/notifications/engine.py` | Implémentation de `send_email` utilisant `smtplib` en asynchrone (`asyncio.to_thread`). |
| `breachradar/config/settings.py` | Ajout des variables de configuration `smtp_server`, `smtp_port`, etc. |

#### Décisions techniques prises

1. **Dashboard UI** : L'utilisation de Vanilla CSS avec un focus sur les micro-interactions, le mode sombre et le glassmorphism permet d'obtenir un rapport final très professionnel sans dépendre de lourds frameworks Javascript, ce qui est critique pour un rapport portable.
2. **Pastebin Monitor** : En l'absence de l'API Scraping officielle de Pastebin (nécessitant un compte Pro "Lifetime"), l'outil s'appuie sur `psbdmp.ws` pour identifier les fuites potentielles.
3. **SMTP asynchrone** : Afin de ne pas introduire de nouvelles dépendances, le module `smtplib` natif de Python est utilisé, exécuté de manière non-bloquante via `asyncio.to_thread`.

#### Prochaines tâches (Phase 4)

1. Audit sécurité (bandit, semgrep).
2. Rotation automatique des clés API.
3. Chiffrement des rapports (Fernet).
4. Dashboard web (FastAPI + HTMX).
5. Documentation mkdocs.
6. Alertes PagerDuty / OpsGenie.

---

### Itération 6 — 2026-04-30 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Exécution de la Phase 3. Implémentation du monitoring continu avec Telegram, IntelX, un Webhook GitHub et l'unification Docker.

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `breachradar/clients/telegram_monitor.py` | Client Telethon pour interroger les canaux Telegram. |
| `breachradar/clients/intelx.py` | Client Intelligence X complet avec logique de polling (attente des résultats). |
| `breachradar/clients/github_webhook.py` | Serveur `aiohttp` léger pour réceptionner les Webhooks GitHub (Secret Scanning). |
| `breachradar/main.py` | Ajout du lancement asynchrone du serveur Webhook GitHub via la commande `schedule`. |
| `breachradar/report/engine.py` | Ajout de la méthode `_generate_pdf` s'appuyant sur WeasyPrint. |
| `docker-compose.yml` | Ouverture du port 8080 pour le Webhook. La stack est désormais totalement unifiée. |

#### Décisions techniques prises

1. **Telegram Monitor** : Utilisation de Telethon. Le fichier gère la nécessité d'une authentification manuelle préalable (création du fichier `.session`) avant de tenter des recherches pour éviter des erreurs silencieuses.
2. **GitHub Webhook** : Utilisation de `aiohttp.web` (déjà dans les dépendances) pour créer un petit serveur intégré sur le port 8080. Il valide la signature HMAC (`X-Hub-Signature-256`) pour des raisons de sécurité.
3. **Export PDF** : Repose sur `WeasyPrint` avec un fallback vers le HTML standard en cas d'absence de la dépendance (qui requiert souvent des librairies C système).
4. **Docker Full Stack** : Le conteneur principal (`breachradar`) se lance désormais via `python -m breachradar schedule`, gérant ainsi les scans cron ET le webhook serveur en tâche de fond continue.

#### Prochaines tâches (Phase 4 - Validation Globale)

1. Rédiger le guide `QUICKSTART.md` détaillant la configuration `.env` et le lancement `docker-compose up`.
2. L'utilisateur procèdera aux tests manuels de bout-en-bout pour valider la stabilité de l'outil.
3. Les retours de tests serviront à corriger les éventuels bugs avant d'entamer la Phase 5 (Hardening).

---

## Points de vigilance pour la prochaine IA

### ⚠️ Règle critique RansomLook
L'alerte ransomware doit être déclenchée **IMMÉDIATEMENT** à la détection, sans attendre
la fin du scan complet. Voir `RansomwareTracker.run()` dans `ransom_tracker.py`.
La sévérité globale du rapport est toujours CRITICAL si un RansomFinding est présent.

### ⚠️ HIBP Rate Limiting
L'API HIBP impose **1 requête par 1500ms** par clé API. Le client doit implémenter
un délai respectueux (pas de parallélisme pour les requêtes email individuelles).
Le Domain Search (scan complet) requiert un abonnement séparé (~550 USD/an).

### ⚠️ Sanitizer — Exception RansomLook
Les données RansomLook sont **publiques par nature** (publiées par les groupes ransomware
eux-mêmes). Le sanitizer NE les masque PAS. Seuls les passwords/hashs/tokens provenant
des autres sources sont sanitisés.

### ⚠️ Tests de sécurité
Le test `test_ransomlook_onion_url_not_in_report()` doit vérifier qu'aucune URL `.onion`
n'apparaît dans le rapport final, même si elle est stockée dans le RansomFinding.

### ⚠️ Docker — RansomLook URL
- En mode local : `RANSOMLOOK_URL=http://localhost:8888`
- En mode Docker (inter-container) : `RANSOMLOOK_URL=http://ransomlook-app:8888`
- Le `docker-compose.yml` injecte automatiquement `RANSOMLOOK_URL=http://ransomlook-app:8888`
  dans le container BreachRadar.

### ⚠️ Structure des fichiers créés
Vérifier que `breachradar/report/templates/` existe avant de créer les templates Jinja2.
Utiliser `Path(__file__).parent / "templates"` pour référencer les templates de manière portable.

---

## Architecture des dépendances (ordre de création recommandé)

```
models/ (pas de dépendances)
  └── finding.py
  └── ransom.py
  └── report.py

config/ (dépend de pydantic-settings)
  └── settings.py
  └── sources.yaml
  └── group_names.yaml

clients/ (dépend de models + config)
  └── base.py
  └── ransomlook.py
  └── hibp.py           ← itération 2
  └── github_monitor.py ← itération 2

core/ (dépend de clients + models)
  └── sanitizer.py
  └── aggregator.py
  └── ransom_tracker.py
  └── orchestrator.py   ← itération 2
  └── scheduler.py      ← itération 2

report/ (dépend de core + models)
  └── engine.py         ← itération 2
  └── templates/        ← itération 2

notifications/ (dépend de models + config)
  └── engine.py         ← itération 2

main.py (dépend de tout)  ← itération 2
```
