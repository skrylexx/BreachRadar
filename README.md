# 🔍 LeakMonitor

> **Outil de détection de fuites de données ciblé sur un domaine.**
> Usage légal — surveillance défensive de votre propre domaine uniquement.
> Cadre : OSINT défensif — RGPD Art. 6.1.f (intérêt légitime)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## Présentation

LeakMonitor détecte si des données appartenant à un domaine (`@mondomaine.fr`) ont été compromises, en agrégeant plusieurs sources publiques et APIs légitimes, et produit un **rapport neutre sans donnée sensible exposée**.

**Deux dimensions complémentaires :**

| Dimension | Description | Sources |
|---|---|---|
| **Backward-looking** | Fuites passées dans des breaches connues | HIBP, LeakCheck, Dehashed, IntelX |
| **Forward-looking** | Early Warning ransomware — domaine listé avant publication | **RansomLook** (gratuit, Docker) |

> ⚠️ **RansomLook** est la seule source capable de détecter une compromission massive *en cours*, avant que les données ne soient publiées. Fenêtre de réaction typique : 5 à 30 jours.

---

## Architecture technique

```
┌──────────────────────────────────────────────────────────┐
│                       LeakMonitor                         │
│                                                           │
│  ┌───────────┐   ┌─────────────────┐   ┌──────────────┐  │
│  │ Scheduler │──▶│  Orchestrator   │──▶│Report Engine │  │
│  │ APSchedul.│   │  (Async Core)   │   │(Jinja2+JSON) │  │
│  └───────────┘   └────────┬────────┘   └──────────────┘  │
│                            │                              │
│          ┌─────────────────┼──────────────┐              │
│          ▼                 ▼              ▼              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐    │
│  │ API Clients  │  │Feed Monitor │  │RansomLook    │    │
│  │ HIBP         │  │Pastebin     │  │Client        │    │
│  │ LeakCheck    │  │GitHub       │  │→ Docker:8888 │    │
│  │ Dehashed...  │  │Telegram/RSS │  └──────────────┘    │
│  └──────────────┘  └─────────────┘                      │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Sanitizer / Anonymizer Layer              │    │
│  │  (Masquage passwords, hashs, tokens, sauf ransom) │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### Flux de données
```
1. Scheduler déclenche le scan
2. Orchestrator charge la config (domaine, sources, clés API)
3. Modules appelés en parallèle (asyncio)
   3c. RansomLook → Si trouvé : ALERTE CRITIQUE immédiate
4. Sanitizer appliqué sur toutes les données brutes
5. Aggregator déduplique + fusionne (RansomFinding → sévérité CRITICAL)
6. Report Engine génère JSON + Markdown + HTML
7. Données brutes purgées de la mémoire
8. (Optionnel) Notification email/webhook
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| Langage | Python 3.12+ |
| HTTP async | httpx 0.27+ |
| Validation | Pydantic v2 |
| Scheduling | APScheduler 3.x |
| CLI | Typer |
| Console | Rich |
| Retry | Tenacity |
| Tests | pytest + pytest-asyncio + respx |
| Linter | ruff + mypy |
| Package manager | uv |
| Containerisation | Docker + Compose v2 |

---

## Prérequis

- Python 3.12+
- **uv** :
  ```bash
  # Linux/macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Docker + Docker Compose v2** :
  ```bash
  docker --version        # >= 24.x
  docker compose version  # >= 2.x
  ```

---

## Installation

```bash
# Cloner le projet
git clone https://github.com/yourorg/leakmonitor.git
cd leakmonitor

# Installer les dépendances Python
uv sync

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env : TARGET_DOMAIN, clés API, RANSOMLOOK_SEARCH_TERMS
```

---

## Démarrage RansomLook (requis — gratuit)

```bash
# Premier démarrage (peuplement initial 10-30 min)
docker compose up ransomlook-redis ransomlook-tor ransomlook-app -d

# Surveiller le scraping
docker compose logs -f ransomlook-app

# Vérifier l'API
curl http://localhost:8888/api/v1/stats

# Tester votre domaine
curl "http://localhost:8888/api/v1/victim?name=mondomaine.fr"
```

---

## Utilisation

### Docker (complet)
```bash
docker compose up -d
```

### Mode développement
```bash
# Scan complet
uv run python -m leakmonitor scan

# Vérification d'urgence RansomLook
uv run python -m leakmonitor ransomlook --check

# Rapport complet (JSON + MD + HTML)
uv run python -m leakmonitor scan --format markdown,json,html

# Email spécifique
uv run python -m leakmonitor check --email alice@mondomaine.fr

# Scheduler en arrière-plan
uv run python -m leakmonitor schedule --start
```

### Commandes Make
```bash
make install          # Installer les dépendances
make test             # Tests unitaires (>80% coverage)
make test-ransomlook  # Tests spécifiques RansomLook
make lint             # Linter ruff
make scan             # Scan complet
make scan-ransom      # Scan RansomLook uniquement
make ransomlook-up    # Démarrer Docker RansomLook
make ransomlook-check # Vérifier l'état de l'instance
make clean            # Nettoyer rapports et caches
```

---

## Configuration des clés API

Voir [`.env.example`](.env.example) pour la liste complète.

| Clé | Source | Coût | Priorité |
|---|---|---|---|
| `HIBP_API_KEY` | haveibeenpwned.com/API/Key | ~3,50 USD/mois | **Indispensable** |
| `GITHUB_TOKEN` | github.com/settings/tokens | Gratuit | **Indispensable** |
| `URLSCAN_API_KEY` | urlscan.io | Gratuit | **Indispensable** |
| `OTX_API_KEY` | otx.alienvault.com | Gratuit | **Indispensable** |
| `RANSOMLOOK_URL` | Instance Docker locale | Gratuit | **Indispensable** |
| `LEAKCHECK_API_KEY` | leakcheck.io | ~10 USD/mois | Très recommandé |
| `DEHASHED_API_KEY` | dehashed.com | ~5 USD/mois | Très recommandé |

---

## Arborescence

```
leakmonitor/
├── README.md
├── ROADMAP.md
├── pyproject.toml
├── Makefile
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── leakmonitor/
│   ├── __init__.py
│   ├── main.py                # CLI (Typer)
│   ├── config/
│   │   ├── settings.py        # Pydantic Settings
│   │   ├── sources.yaml
│   │   └── group_names.yaml
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── sanitizer.py
│   │   ├── aggregator.py
│   │   ├── ransom_tracker.py
│   │   └── scheduler.py
│   ├── clients/
│   │   ├── base.py
│   │   ├── hibp.py
│   │   ├── leakcheck.py
│   │   ├── dehashed.py
│   │   ├── intelx.py
│   │   ├── github_monitor.py
│   │   ├── urlscan.py
│   │   ├── otx.py
│   │   └── ransomlook.py
│   ├── resolver/
│   │   └── email_resolver.py
│   ├── models/
│   │   ├── finding.py
│   │   ├── ransom.py
│   │   └── report.py
│   ├── report/
│   │   ├── engine.py
│   │   └── templates/
│   │       ├── report.md.j2
│   │       ├── report.html.j2
│   │       └── notification.txt.j2
│   └── notifications/
│       └── engine.py
├── tests/
│   ├── conftest.py
│   ├── test_sanitizer.py
│   ├── test_aggregator.py
│   ├── test_ransom_tracker.py
│   ├── test_security.py
│   ├── test_clients/
│   │   ├── test_hibp.py
│   │   ├── test_ransomlook.py
│   │   └── test_github.py
│   └── fixtures/
│       └── ransomlook/
│           ├── victim_found.json
│           └── victim_not_found.json
└── reports/
    └── .gitkeep
```

---

## Sécurité — Garanties

- ❌ Aucun mot de passe, hash ou credential stocké
- ❌ Aucune URL .onion dans les rapports
- ✅ Sanitizer appliqué sur toutes les données brutes (hors RansomLook — données publiques)
- ✅ Données temporaires purgées en mémoire après génération du rapport
- ✅ Clés API uniquement dans `.env` (jamais committées)
- ✅ RansomLook exposé uniquement sur `127.0.0.1:8888` (jamais `0.0.0.0`)

---

## Cadre légal

| Ce projet FAIT | Ce projet NE FAIT PAS |
|---|---|
| Requêtes sur APIs publiques légitimes | Accès à des systèmes non autorisés |
| Surveillance de votre propre domaine | Surveillance de domaines tiers |
| Traitement en mémoire uniquement | Stockage de données personnelles |
| Rapport sans données sensibles | Revente ou partage des découvertes |

**Base légale** : RGPD Art. 6.1.f (intérêt légitime) + Directive NIS2 (transposée fin 2024).

> ⚠️ L'utilisation sur des domaines ne vous appartenant pas peut constituer une infraction au Code Pénal (Art. 323-1) et au RGPD.

---

## Collaboration IA (protocole handoff)

Ce projet est développé en mode **Human + AI pair programming**.  
Pour reprendre après une interruption :

```
Lis le README.md pour comprendre l'architecture et le ROADMAP.md pour savoir
où la dernière IA s'est arrêtée. Reprends la suite en respectant le même protocole.
```
