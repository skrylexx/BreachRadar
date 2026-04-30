# ROADMAP — BreachRadar

> Journal de bord structuré — mis à jour à chaque itération IA ou humaine.
> **Protocole handoff** : Lire ce fichier + README.md avant toute contribution.

---

## Avancement global

```
Phase 1 — MVP    [██████████] 100%
Phase 2          [██████████] 100%
Phase 3          [██████████] 100%
Phase 4          [░░░░░░░░░░]  0%
Phase 5          [░░░░░░░░░░]  0%
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

### Phase 4 — Validation Globale & Tests Manuels
- [ ] Création du guide `QUICKSTART.md` (lancement de la stack)
- [ ] Lancement de la stack Docker unifiée
- [ ] Vérification de bout-en-bout (Orchestrateur, Webhook, PDF)

### Phase 5 — Hardening
- [ ] Audit sécurité (bandit, semgrep)
- [ ] Rotation automatique des clés API
- [ ] Chiffrement des rapports (Fernet)
- [ ] Dashboard web (FastAPI + HTMX)
- [ ] Documentation mkdocs
- [ ] Alertes PagerDuty / OpsGenie

---

## CHANGELOG

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
