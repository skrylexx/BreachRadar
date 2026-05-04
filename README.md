# 🔍 BreachRadar WebUI

![Logo **Breach**Radar](images/logo.png)

> **Plateforme Web de détection de fuites de données ciblée sur un domaine.**
> Usage légal — surveillance défensive de votre propre domaine uniquement.
> Cadre : OSINT défensif — RGPD Art. 6.1.f (intérêt légitime)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

---

## Présentation

BreachRadar détecte si des données appartenant à un domaine (`@mondomaine.fr`) ont été compromises, en agrégeant plusieurs sources publiques et APIs légitimes, et produit un **rapport neutre sans donnée sensible exposée** directement dans une interface web dédiée (WebUI).

**Deux dimensions complémentaires :**

| Dimension | Description | Sources |
|---|---|---|
| **Backward-looking** | Fuites passées dans des breaches connues | HIBP, LeakCheck, Dehashed, IntelX |
| **Forward-looking** | Early Warning ransomware — domaine listé avant publication | **RansomLook** (gratuit, Docker) |

> ⚠️ **RansomLook** est la seule source capable de détecter une compromission massive *en cours*, avant que les données ne soient publiées. Fenêtre de réaction typique : 5 à 30 jours.

---

## Architecture technique

BreachRadar fonctionne avec une architecture micro-services complète, englobant une application web riche et un moteur asynchrone performant.

### Stack WebUI & Moteur

| Couche | Technologie |
|---|---|
| **Frontend** | Next.js 15 + Shadcn/UI + Tailwind CSS |
| **Backend (Moteur)** | FastAPI (Python 3.12) |
| **Base de données** | PostgreSQL 16 |
| **Cache / Sessions** | Redis 7 |
| **Authentification** | JWT HttpOnly Cookies |
| **MFA** | TOTP RFC 6238 (Google Auth, Authy, Microsoft Auth) |
| **Scheduling** | APScheduler 3.x (intégré dans FastAPI) |
| **Package manager** | uv (Backend), npm (Frontend) |

---

## Prérequis

- **Docker + Docker Compose v2** (Pour l'exécution simplifiée) :
  ```bash
  docker --version        # >= 24.x
  docker compose version  # >= 2.x
  ```
- *Optionnel (Développement)* : Python 3.12+, `uv`, Node.js 20+

---

## Démarrage Rapide (Production)

L'outil s'exécute intégralement via Docker. Il n'y a plus d'interface en ligne de commande (CLI), tout est pilotable depuis la WebUI.

```bash
# 1. Cloner le projet
git clone https://github.com/yourorg/breachradar.git
cd breachradar

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API et définir des mots de passe sécurisés 
# (UI_DB_PASSWORD, UI_REDIS_PASSWORD, UI_JWT_SECRET, UI_ADMIN_EMAIL, UI_ADMIN_PASSWORD)

# 3. Lancer la plateforme
docker compose up -d

# 4. Accéder à l'interface
# Ouvrez votre navigateur sur http://localhost:3000
```

> **Note sur RansomLook** : Au premier démarrage, RansomLook (inclus dans la stack) a besoin de 10 à 30 minutes pour accomplir son scraping initial via Tor. Vous pouvez consulter les logs avec `docker compose logs -f ransomlook-app`.

---

## Configuration des clés API

Voir [`.env.example`](.env.example) pour la liste complète.

| Clé | Source | Coût | Priorité |
|---|---|---|---|
| `TARGET_DOMAIN` | Le domaine que vous surveillez | Gratuit | **Obligatoire** |
| `HIBP_API_KEY` | haveibeenpwned.com/API/Key | ~3,50 USD/mois | **Indispensable** |
| `GITHUB_TOKEN` | github.com/settings/tokens | Gratuit | **Indispensable** |
| `URLSCAN_API_KEY` | urlscan.io | Gratuit | **Indispensable** |
| `OTX_API_KEY` | otx.alienvault.com | Gratuit | **Indispensable** |
| `LEAKCHECK_API_KEY` | leakcheck.io | ~10 USD/mois | Très recommandé |
| `DEHASHED_API_KEY` | dehashed.com | ~5 USD/mois | Très recommandé |

---

## Arborescence du Projet

L'arborescence a été simplifiée pour une architecture 100% WebUI.

```
breachradar/
├── README.md                 # Ce fichier
├── ROADMAP.md                # Suivi de projet
├── Makefile                  # Raccourcis commandes de dev
├── .env.example              # Variables d'environnement unifiées
├── docker-compose.yml        # Stack complète (Postgres, Redis, API, UI, RansomLook)
│
├── backend/                  # API FastAPI + Moteur BreachRadar
│   ├── Dockerfile
│   ├── pyproject.toml        # Dépendances (uv)
│   ├── tests/                # Tests unitaires
│   └── app/
│       ├── main.py           # Point d'entrée FastAPI
│       ├── core/             # Configuration globale (Settings), init DB
│       ├── clients/          # Connecteurs (HIBP, GitHub, RansomLook...)
│       ├── engine/           # Cœur métier (Orchestrateur, Scheduler, Sanitizer)
│       ├── models/           # Modèles SQLAlchemy (Users) & Pydantic (Findings)
│       ├── routers/          # Endpoints API (Scans, Users, Auth, Webhooks)
│       └── services/         # Notifications, Reports, Resolvers
│
└── frontend/                 # Application Next.js
    ├── Dockerfile
    ├── package.json
    ├── tailwind.config.ts
    └── src/
        ├── app/              # Routage App Router (Next 15)
        ├── components/       # Composants réutilisables (Shadcn, Recharts)
        └── lib/              # Utilitaires (api.ts, i18n)
```

---

## Gouvernance SOC et RBAC

BreachRadar intègre une gestion des rôles stricte pour répondre aux exigences SOC.

| Action | Admin | Viewer |
|---|---|---|
| Voir le dashboard principal | ✅ | ✅ |
| Consulter l'historique des alertes | ✅ | ✅ |
| Exporter les rapports (PDF, CSV) | ✅ | ✅ |
| Déclencher un scan manuel | ✅ | ❌ |
| Modifier la configuration (Clés API, SMTP) | ✅ | ❌ |
| Gérer les utilisateurs (RBAC) | ✅ | ❌ |
| Accéder aux Audit Logs complets | ✅ | ❌ |

---

## Sécurité — Garanties

- ❌ Aucun mot de passe, hash ou credential stocké en clair.
- ❌ Aucune URL .onion dans les rapports exportés.
- ✅ Sanitizer appliqué sur toutes les données brutes avant l'affichage ou le stockage en base.
- ✅ Données temporaires purgées en mémoire après traitement.
- ✅ Clés API uniquement dans `.env` ou chiffrées en base (Fernet).
- ✅ RansomLook exposé uniquement sur le réseau Docker interne (jamais `0.0.0.0`).
- ✅ Authentification forte (JWT HttpOnly + MFA obligatoire pour Admin).

---

## Cadre légal

| Ce projet FAIT | Ce projet NE FAIT PAS |
|---|---|
| Requêtes sur APIs publiques légitimes | Accès à des systèmes non autorisés |
| Surveillance de votre propre domaine | Surveillance de domaines tiers |
| Traitement en mémoire et DB sécurisée | Stockage prolongé de données personnelles |
| Rapport sans données sensibles | Revente ou partage des découvertes |

**Base légale** : RGPD Art. 6.1.f (intérêt légitime) + Directive NIS2 (transposée fin 2024).

> ⚠️ L'utilisation sur des domaines ne vous appartenant pas peut constituer une infraction au Code Pénal (Art. 323-1) et au RGPD.
