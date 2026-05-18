# BreachRadar — Backend API

Ce dossier contient le cœur de l'application BreachRadar : l'API FastAPI et le moteur d'orchestration OSINT.

## 🚀 Technologies utilisées

- **Langage** : Python 3.12+
- **Framework Web** : [FastAPI](https://fastapi.tiangolo.com/) (Asynchrone)
- **Base de données** : PostgreSQL avec [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Asyncio)
- **Migrations** : [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Schémas** : [Pydantic v2](https://docs.pydantic.dev/)
- **Sécurité** : JWT (HS256), BCrypt, MFA TOTP ([PyOTP](https://github.com/pyauth/pyotp))
- **Gestion des tâches** : [APScheduler](https://apscheduler.agronholm.net/) pour les scans planifiés
- **Cache & Rate Limiting** : [Redis](https://redis.io/) avec [SlowAPI](https://github.com/laurentS/slowapi)
- **Gestion des dépendances** : [uv](https://github.com/astral-sh/uv) & `pyproject.toml`

## 🛠️ Utilités du Backend

1. **Orchestration des scans** : Pilote les différents modules de recherche (HIBP, GitHub, RansomLook, etc.).
2. **Système CVE** : Surveille en temps réel les vulnérabilités via les flux NVD (NIST) et OSV.dev.
3. **Gestion Utilisateurs** : Authentification sécurisée, rôles (Admin/Viewer), et gestion du MFA.
4. **Génération de rapports** : Agrégation des résultats de scan en rapports HTML, Markdown ou PDF.
5. **Webhooks** : Endpoint de réception pour les alertes externes (ex: GitHub Secret Scanning).

## 📡 Endpoints principaux

L'API est documentée via Swagger UI à l'adresse `/docs` (en mode développement).

- `/auth` : Authentification, rafraîchissement de token, vérification MFA.
- `/users` : Gestion des comptes utilisateurs et profils.
- `/scans` : Déclenchement manuel et historique des scans de domaine.
- `/api/v1/dashboard` : Statistiques agrégées pour les graphiques du frontend.
- `/api/v1/cve` : Consultation et filtrage des vulnérabilités détectées.
- `/api/v1/ransomlook` : Données de surveillance des groupes de ransomware.
- `/api/v1/settings` : Configuration globale, gestion des clés API OSINT.
- `/webhooks` : Réception d'alertes externes.

## 💻 Installation locale (sans Docker)

Si vous souhaitez lancer le backend nativement pour le développement :

### 1. Prérequis
- Python 3.12 installé.
- Une instance **PostgreSQL** active (créer une DB `breachradar`).
- Une instance **Redis** active.

### 2. Setup de l'environnement
```bash
# Se placer dans le dossier backend
cd backend

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
.\venv\Scripts\activate
# Sur Linux/macOS :
source venv/bin/activate

# Installer les dépendances en mode éditable
pip install -e .[dev]
```

### 3. Configuration
Assurez-vous d'avoir un fichier `.env` à la racine du projet (BreachRadar/) avec les variables nécessaires (voir `.env.example`).

### 4. Lancement
```bash
# Lancer l'API avec auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
L'API sera accessible sur [http://localhost:8000](http://localhost:8000).

## 🧪 Tests & Qualité
```bash
# Lancer les tests
pytest

# Vérification du typage
mypy .

# Linting
ruff check .
```
