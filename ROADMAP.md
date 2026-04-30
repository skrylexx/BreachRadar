# ROADMAP — LeakMonitor

> Journal de bord structuré — mis à jour à chaque itération IA ou humaine.
> **Protocole handoff** : Lire ce fichier + README.md avant toute contribution.

---

## Avancement global

```
Phase 1 — MVP    [██████████] 100%
Phase 2          [░░░░░░░░░░]  0%
Phase 3          [░░░░░░░░░░]  0%
Phase 4          [░░░░░░░░░░]  0%
```

---

## Vision globale

### Phase 1 — MVP (en cours)
**Objectif** : Infrastructure de base fonctionnelle, sources gratuites prioritaires, rapport complet avec section ransomware.

- [x] README.md et ROADMAP.md
- [x] pyproject.toml (dépendances)
- [x] .env.example (template configuration)
- [x] .gitignore
- [x] docker-compose.yml (LeakMonitor + RansomLook stack complète)
- [x] Dockerfile
- [x] Makefile
- [x] leakmonitor/models/finding.py (LeakFinding, Severity)
- [x] leakmonitor/models/ransom.py (RansomFinding, RansomStats, RansomStatus)
- [x] leakmonitor/models/report.py (FinalReport, ReportMetadata)
- [x] leakmonitor/config/settings.py (Pydantic Settings)
- [x] leakmonitor/config/sources.yaml
- [x] leakmonitor/config/group_names.yaml
- [x] leakmonitor/clients/base.py (BaseLeakClient ABC)
- [x] leakmonitor/clients/ransomlook.py (RansomLookClient)
- [x] leakmonitor/core/sanitizer.py (DataSanitizer)
- [x] leakmonitor/core/aggregator.py (ResultAggregator)
- [x] leakmonitor/core/ransom_tracker.py (RansomwareTracker)
- [x] leakmonitor/config/source_registry.py (SourceRegistry — disponibilité dynamique)
- [x] SECURITY.md (procédures sécurité complètes)
- [x] .pre-commit-config.yaml (detect-secrets, ruff, hooks git)
- [x] scripts/verify_sanitizer.py (vérification manuelle sanitizer)
- [x] tests/test_source_registry.py (14 tests de disponibilité des sources)
- [x] leakmonitor/clients/hibp.py
- [x] leakmonitor/clients/github_monitor.py
- [x] leakmonitor/core/orchestrator.py
- [x] leakmonitor/core/scheduler.py
- [x] leakmonitor/resolver/email_resolver.py
- [x] leakmonitor/report/engine.py
- [x] leakmonitor/report/templates/report.md.j2
- [x] leakmonitor/report/templates/report.html.j2
- [x] leakmonitor/report/templates/notification.txt.j2
- [x] leakmonitor/notifications/engine.py
- [x] leakmonitor/main.py (CLI Typer)
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
- [ ] leakmonitor/clients/leakcheck.py
- [ ] leakmonitor/clients/dehashed.py
- [ ] leakmonitor/clients/pastebin_monitor.py
- [ ] Domain Email Resolver (Hunter.io + theHarvester)
- [ ] Rapport HTML avec dashboard visuel
- [ ] Scheduler + notifications email

### Phase 3 — Monitoring continu
- [ ] leakmonitor/clients/telegram_monitor.py
- [ ] GitHub webhook monitoring
- [ ] leakmonitor/clients/intelx.py
- [ ] Docker full stack (un seul `docker compose up`)
- [ ] Export PDF

### Phase 4 — Hardening
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
| `docker-compose.yml` | Stack complète : LeakMonitor + RansomLook (app + redis + tor) |
| `Dockerfile` | Image Python 3.12-slim, non-root, uv optimisé |
| `Makefile` | Toutes les commandes du cahier des charges |
| `leakmonitor/__init__.py` | Package init avec version |
| `leakmonitor/models/finding.py` | LeakFinding, Severity, EmailFindingResult |
| `leakmonitor/models/ransom.py` | RansomFinding, RansomStats, RansomStatus |
| `leakmonitor/models/report.py` | FinalReport, ReportMetadata, SeverityBreakdown |
| `leakmonitor/config/settings.py` | Pydantic Settings — validation complète |
| `leakmonitor/config/sources.yaml` | Activation/désactivation de chaque source |
| `leakmonitor/config/group_names.yaml` | Mapping 40+ groupes ransomware |
| `leakmonitor/clients/base.py` | BaseLeakClient ABC — interface commune |
| `leakmonitor/clients/ransomlook.py` | RansomLookClient complet avec retry + dedup |
| `leakmonitor/core/sanitizer.py` | DataSanitizer — masquage données sensibles |
| `leakmonitor/core/aggregator.py` | ResultAggregator — dédup + sévérité |
| `leakmonitor/core/ransom_tracker.py` | RansomwareTracker — orchestration + alerte immédiate |
| `reports/.gitkeep` | Répertoire de sortie (gitignored) |

#### Décisions techniques prises

1. **uv** choisi comme package manager (plus rapide que pip/poetry, recommandé dans le CdC).
2. **RansomLookClient** intègre la déduplication par `(group_name, post_title, published)` pour éviter les doublons multi-termes.
3. **DataSanitizer** couvre 9 patterns sensibles : passwords, MD5/SHA-1/SHA-256/bcrypt, tokens API, base64.
4. **ResultAggregator** : un seul RansomFinding élève la sévérité GLOBALE à CRITICAL (règle métier du CdC).
5. **RansomwareTracker** : l'alerte immédiate est déclenchée AVANT la fin du scan complet (fenêtre de réaction critique).
6. **BaseLeakClient** : interface ABC avec `check_email` et `check_domain` + rate limiter intégré.

#### Prochaines tâches (priorité pour l'itération suivante)

1. **`leakmonitor/clients/hibp.py`** — Client HIBP avec k-anonymity pour les passwords + rate limit 1500ms
2. **`leakmonitor/clients/github_monitor.py`** — Recherche de credentials hardcodés dans les repos publics
3. **`leakmonitor/core/orchestrator.py`** — Chef d'orchestre : asyncio.gather() sur tous les clients
4. **`leakmonitor/main.py`** — CLI Typer avec les commandes : scan, ransomlook, check, schedule, sources
5. **`leakmonitor/report/engine.py`** — Générateur de rapports Jinja2 (MD + JSON)
6. **`tests/test_sanitizer.py`** + **`tests/test_ransom_tracker.py`** — Tests unitaires prioritaires

---

### Itération 3 — 2026-04-30 (Gemini 3.1 Pro — Antigravity)

**Objectif de l'itération** : Finalisation de la Phase 1 (MVP à 100%) en implémentant l'orchestrateur, le reporting complet et les clients manquants (HIBP, GitHub).

#### Fichiers créés/modifiés

| Fichier | Description |
|---|---|
| `leakmonitor/clients/hibp.py` | Implémentation du client HIBP (Rate Limiting de 1.5s, support K-Anonymity pour MDP) |
| `leakmonitor/clients/github_monitor.py` | Recherche de mentions de domaines et d'emails sur GitHub (gestion d'API anonyme) |
| `leakmonitor/core/orchestrator.py` | Orchestration parallèle des clients avec `asyncio.gather` |
| `leakmonitor/core/scheduler.py` | Placeholder en prévision de la Phase 2 |
| `leakmonitor/resolver/email_resolver.py` | Résolveur initial (liste commune de préfixes et lecture fichier `emails.txt`) |
| `leakmonitor/report/engine.py` | Générateur de rapports exploitant Jinja2 pour Markdown/HTML et Pydantic pour le JSON |
| `leakmonitor/report/templates/report.*.j2` | 3 templates Jinja2 (Markdown, HTML, Texte/Notification) respectant la RGPD |
| `leakmonitor/notifications/engine.py` | Envoi d'alertes webhook pour les compromissions critiques RansomLook |
| `leakmonitor/main.py` | Interface ligne de commande basée sur `typer` (`scan`, `check`, `ransomlook`, `sources`, etc.) |
| `tests/test_clients/test_*.py` | Tests unitaires pour les clients HIBP et RansomLook |

#### Décisions techniques prises

1. **Typer CLI** : Adopté pour fournir une interface élégante et robuste dans `main.py` en exploitant `asyncio.run()`.
2. **Templating Jinja2** : Les rapports Markdown et HTML partagent un filtre `mask_onion` garantissant qu'aucune URL `.onion` brute ne soit insérée dans le rendu final.
3. **Rate Limiting** : `HIBPClient` intègre un délai explicite de 1.5 seconde avant requête et `GitHubClient` de 2.0 secondes. L'orchestrateur lance les scans sur une liste d'emails en traitant par lots sans bloquer la boucle asynchrone globale.
4. **Email Resolver** : Une base simple en phase 1 pour tester rapidement, avant l'arrivée de theHarvester en phase 2.

#### Prochaines tâches (Phase 2)

1. Implémenter les clients de sources payantes : `leakcheck.py`, `dehashed.py`.
2. Résolveur avancé avec OSINT Tools (theHarvester, Hunter.io).
3. Intégration d'un vrai scheduler (`APScheduler`) dans `leakmonitor/core/scheduler.py`.
4. Tests complets pour l'Agrégateur et l'Orchestrateur.

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
  dans le container LeakMonitor.

### ⚠️ Structure des fichiers créés
Vérifier que `leakmonitor/report/templates/` existe avant de créer les templates Jinja2.
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
