# Architecture de BreachRadar

Ce document détaille l'organisation du dépôt BreachRadar, les responsabilités de chaque module, la localisation des fichiers de configuration et les protocoles dédiés aux agents IA.

## 🏗️ Vue d'ensemble du Projet

BreachRadar est une plateforme de veille cyber structurée en trois piliers principaux :
1.  **Backend (FastAPI)** : Moteur de collecte (OSINT), agrégation de données et API REST.
2.  **Frontend (Next.js)** : Interface utilisateur moderne pour la visualisation des alertes et la gestion de la configuration.
3.  **Services Tiers (Docker)** : Stack incluant Redis, PostgreSQL, Tor et RansomLook.

---

## 📁 Arborescence Détaillée

### 🔹 `/backend` — Le Cœur du Système
Contient toute la logique métier, les collecteurs OSINT et l'API.

*   `backend/app/main.py` : Point d'entrée de l'application FastAPI.
*   `backend/app/core/` : Configuration globale (`config.py`), connexion base de données (`database.py`), sécurité (`security.py`) et registres de sources.
*   `backend/app/engine/` : Moteur d'exécution.
    *   `orchestrator.py` : Coordonne les scans et les collecteurs.
    *   `aggregator.py` : Fusionne et dédoublonne les résultats.
    *   `scheduler.py` : Gère les tâches planifiées.
*   `backend/app/clients/` : Clients API pour les sources externes (HIBP, IntelX, Dehashed, RansomLook, etc.).
*   `backend/app/models/` : Définitions des tables SQL (SQLAlchemy).
*   `backend/app/routers/` : Endpoints de l'API REST organisés par domaine (auth, scans, cve, dashboard).
*   `backend/app/schemas/` : Modèles de validation de données (Pydantic) pour les requêtes/réponses API.
*   `backend/tests/` : Suite de tests unitaires et d'intégration utilisant `pytest`.

### 🔹 `/frontend` — L'Interface Utilisateur
Application Next.js (App Router) développée en TypeScript.

*   `frontend/src/app/` : Structure des pages et layouts (Dashboard, Login, Admin).
*   `frontend/src/components/` : Composants UI réutilisables (shadcn/ui, tableaux, graphiques).
*   `frontend/src/lib/` : Utilitaires, gestion du store (Zustand/Context) et client API.
*   `frontend/messages/` : Fichiers de traduction (i18n) en français et anglais.

### 🔹 `/ransomlook_config`
Contient les scripts et fichiers de configuration spécifiques à l'intégration de RansomLook (monitoring des groupes ransomware).
*   `start_local.sh` : Script de démarrage du service dans Docker.
*   `patch_api.py` / `patch_redis.py` : Scripts utilitaires pour ajuster le comportement de RansomLook.

### 🔹 `/security_audits`
Dossier dédié à la documentation de sécurité et aux procédures d'audit.
*   `AUDIT_INSTRUCTIONS.md` : Guide pour mener des audits de sécurité sur le repo.
*   `TECH_STACK.md` : Inventaire technique détaillé et état de sécurité des composants.

---

## ⚙️ Configuration

Le projet utilise des variables d'environnement pour sa configuration.

| Type | Fichier | Description |
| :--- | :--- | :--- |
| **Global** | `.env` | Variables d'environnement (secrets, API keys, URLs services). Voir `.env.example`. |
| **Backend** | `backend/app/core/config.py` | Chargement et validation des variables via Pydantic Settings. |
| **Docker** | `docker-compose.yml` | Orchestration des conteneurs (ports, réseaux, volumes). |
| **Frontend** | `frontend/next.config.ts` | Configuration Next.js (CSP, rewrites, headers de sécurité). |
| **Linting/Style** | `.pre-commit-config.yaml` | Hooks de validation avant commit (Ruff, MyPy). |

---

## 🤖 Intelligence Artificielle (Agents IA)

Le dépôt est optimisé pour la collaboration avec des agents IA (Gemini, Claude, GPT). Plusieurs fichiers et dossiers leur sont dédiés :

*   **`AI_AGENT_GUIDE.md`** (Racine) : **Point d'entrée obligatoire.** Contient la mission, les protocoles de traçabilité et les règles de passation entre sessions.
*   **`.gemini/`** : Dossier spécifique à Gemini CLI.
    *   `.gemini/skills/` : Contient des instructions spécialisées ("skills") permettant à l'IA d'agir avec une expertise spécifique sur certains domaines (ex: `python-api-backend`, `nextjs-app-router`).
*   **`AI_AGENT_GUIDE.md`** remplace les anciens fichiers `AGENT.md` et `IA_CHANGE.md` pour centraliser le pilotage.

---

## 📈 Gestion de Projet et Suivi

*   **`ROADMAP.md`** : Contient l'état d'avancement du projet, les tâches à venir et le **CHANGELOG** détaillé de chaque session.
*   **`Cahier-Des-Charges_BreachRadar.md`** : Document de référence sur les besoins fonctionnels et techniques initiaux.
*   **`README.md`** : Présentation générale et instructions de déploiement rapide.
*   **`QUICKSTART.md`** : Guide pas-à-pas pour lancer le projet en mode Docker ou Développement local.
*   **`SECURITY_BEST-PRACTICE.md`** : Guide des standards de sécurité à respecter lors du développement.

---

## 🛠️ Outils de Maintenance

*   **`Makefile`** : Raccourcis pour les commandes courantes (build, tests, lint, clean).
*   **`scripts/`** : Scripts utilitaires divers (ex: `verify_sanitizer.py`).
*   **`reports/`** : Dossier de sortie pour les rapports générés par le système (PDF/MD/HTML).
