# Cahier des charges WebUI + CLI — BreachRadar

## 1. Contexte et objectifs

BreachRadar est une plateforme de détection de fuites de données ciblée sur un domaine (ex. `@mondomaine.fr`), combinant :
- une **WebUI** moderne pour les équipes sécurité / gouvernance,
- un **moteur backend asynchrone** pour orchestrer les scans,
- et une **intégration forte avec RansomLook** pour la détection précoce de campagnes ransomware en cours.

Objectifs principaux :
- Offrir un **dashboard Web dense mais lisible**, orienté SOC / gouvernance, non marketing.
- Permettre aux analystes de **visualiser l’état de compromission dans le temps**, par source et globalement.
- Garantir une **mise en œuvre RGPD-by-design** : zéro exposition de secrets, rapports neutres.
- Fournir en parallèle une **CLI d’administration / intégration** (devops, CI, debug).

## 2. Périmètre fonctionnel

Ce cahier des charges couvre :
- la **WebUI** (frontend Next.js + backend FastAPI déjà présents dans le repo),
- la **CLI d’administration** de la plateforme (commande Python ou entrypoint dans le conteneur backend).

Sont exclus (mais décrits dans d’autres documents) :
- le détail complet de chaque source OSINT,
- la description exhaustive des modèles internes,
- la documentation très bas niveau de RansomLook déjà présente dans `Cahier-Des-Charges_BreachRadar.md`.

## 3. Utilisateurs et rôles

### 3.1 Personae

- **Admin / Responsable sécurité**
  - Configure les clés API, SMTP, RansomLook.
  - Gère les utilisateurs et les rôles.
  - Déclenche des scans manuels si besoin.
  - Consomme les rapports PDF pour les comités de gouvernance.

- **Viewer / Analyste SOC**
  - Consulte le dashboard et l’historique.
  - Navigue dans les rapports.
  - Exporte les rapports (PDF, éventuellement CSV).
  - Ne modifie aucune configuration sensible.

### 3.2 RBAC (règles)

- Admin : accès complet, y compris gestion des clés API, SMTP, utilisateurs, paramétrage des scans.
- Viewer : lecture seule sur les dashboards, rapports, historique ; export seulement.

## 4. Architecture & stack technique

### 4.1 Vue d’ensemble

Stack actuelle à formaliser :

- **Frontend WebUI**
  - Next.js 15 (App Router) + TypeScript.
  - Tailwind CSS + Shadcn/UI pour les composants et le thème.
  - Thème dark par défaut, avec switch dark/light.
  - i18n : anglais (par défaut) + français.

- **Backend Web / moteur**
  - FastAPI (Python 3.12).
  - Moteur de scan asynchrone (HTTPX + asyncio).
  - Scheduler APScheduler intégré au backend pour les scans hebdomadaires.

- **Persistence & infra**
  - PostgreSQL 16 :
    - stockage comptes utilisateurs, rôles, sessions applicatives (si besoin),
    - stockage des résultats de scans **sanitisés** (aucune donnée sensible brute).
  - Redis 7 : cache, gestion de sessions et de ratelimiting.
  - RansomLook :
    - soit instance auto-hébergée en Docker sur réseau interne, sans API key,
    - soit utilisation de l’API SaaS `https://www.ransomlook.io/api` (clé d’API dans le header `Authorization`).

- **Authentification & sécurité Web**
  - Authentification : **JWT via cookies HttpOnly**.
  - MFA : TOTP (RFC 6238), compatible Google Authenticator, Authy, Microsoft Authenticator.
  - CSRF protection sur les formulaires sensibles.
  - Rate limiting sur login, relance de scan, export de rapport.
  - Audit trail des actions admin (création user, ajout/retrait de clé API, modification config, relance scan).

### 4.2 Architecture Docker

- `frontend` : Next.js (port 3000).
- `backend` : FastAPI + moteur asynchrone (port interne, ex. 8000).
- `db` : Postgres.
- `redis` : cache, ratelimiting.
- `ransomlook-*` : stack RansomLook (redis/tor/app) si auto-hébergé, reliée au backend par un réseau Docker interne.
- `mail` : SMTP externe ou service de mail selon configuration.

Les conteneurs sont orchestrés par un **docker-compose unique** qui expose uniquement :
- le frontend sur `http://localhost:3000`,
- éventuellement l’API backend en interne pour la CLI.

RansomLook ne doit **jamais** être exposé en 0.0.0.0 ; uniquement sur le réseau interne Docker ou sur `127.0.0.1`.

## 5. WebUI — Principes de design & identité

### 5.1 Style général

- Thématique **cyber / gouvernance**, pas marketing.
- Dark mode par défaut, palette inspirée Shadcn/UI :
  - Fond : `#09090b`.
  - Surfaces (cards, modals) : `#18181b`.
  - Accent “Radar” : bleu cyan/indigo `#38bdf8`.
- Codes couleur de sévérité :
  - Rouge (CRITICAL) / Orange (HIGH) / Jaune (MEDIUM) / Bleu ou gris (LOW).

### 5.2 Typographie

- UI générale : **Inter**.
- Données techniques (hashes, emails, logs, indicateurs) : **JetBrains Mono**.

### 5.3 Layout

- **Sidebar fine** à gauche, uniquement icônes :
  - Dashboard, Scans, API Keys, Users, Changelog/Updates.
- En-tête (header) :
  - Switch langue (EN / FR).
  - Switch dark mode.
  - Profil utilisateur (menu déroulant : profil, MFA, logout).
- Contenu central type “dashboard SOC” :
  - Heatmap / graphique d’évolution globale en haut.
  - Cards de statut API.
  - Tableaux de fuites et d’alertes en bas.

### 5.4 Identité “Radar”

- Élément visuel discret de radar :
  - sur la landing (dashboard principal),
  - et comme animation de chargement lors du lancement d’un scan (spinner type radar).

## 6. WebUI — Pages et parcours

### 6.1 Landing / Dashboard

Objectif : vue synthétique de l’état de sécurité du domaine.

Contenu minimal :

- **Heatmap / graphique global d’évolution** (12 mois par défaut, avec filtres 7j / 1 mois / 6 mois / 12 mois)
  - Axe X : temps.
  - Axe Y : nombre de “problématiques remontées” (findings) tous outils confondus.
  - Représentation en barres ou ligne type NinjaOne.

- **Cards de statut des sources / connecteurs** :
  - HIBP, LeakCheck, Dehashed, GitHub, URLScan, OTX, RansomLook, etc.
  - Chaque card affiche : nom de la source, statut (✅ / ⚠️ / ❌), date du dernier succès, badge de sévérité si RansomLook signale une alerte CRITICAL.
  - Bordure ou “barre latérale” colorée (vert/rouge) pour l’état actif.

- **Bloc “Ransomware / RansomLook” en cas d’alerte** :
  - résumé de la dernière alerte (groupe, date de détection, taille revendiquée, statut),
  - CTA vers la page détaillée “Alertes Ransomware”.

- **Résumé des derniers scans hebdomadaires** :
  - table des scans (date, durée, nb de findings, sévérité globale),
  - timestamps sans secondes (ex. `2026-05-05 10:03`).

- Accès rapide :
  - liens vers la page de chaque outil,
  - lien vers la page “Rapports” globale.

### 6.2 Pages par outil

Une page par source / famille de sources (ex. “HIBP & Breaches”, “GitHub & GitLab”, “RansomLook”).

Pour chaque page :
- filtre temporel (7j / 1 mois / 6 mois / 12 mois / “depuis toujours”),
- **graphique spécifique d’évolution** :
  - Axe X : temps.
  - Axe Y : nb de findings pour cette source uniquement.
- tableau des findings récents :
  - colonnes : date, type (email / domaine / ransomware), sévérité, source, résumé,
  - badges de sévérité colorés,
  - pagination côté serveur.
- bouton “Relancer un scan pour cette source” (Admin uniquement).

### 6.3 Page Rapports

- liste des **rapports de scan** (hebdo + manuels) :
  - date, domaine, sévérité globale, nb d’emails compromis, présence ou non d’alerte RansomLook.
- actions possibles :
  - **Exporter le rapport en PDF**,
  - (optionnel) export JSON / CSV.
- bouton “Générer un rapport global pour la période X” : agrégation de plusieurs scans.

### 6.4 Page Alertes Ransomware (RansomLook)

- section “État de l’instance” : URL utilisée, nb de groupes suivis, nb de posts, dernière mise à jour.
- liste des alertes : groupe (LockBit, BlackCat, etc.), victime/victim_name, pays, secteur, claim_size, statut (LISTED / PUBLISHED), date découverte / publication.
- actions : filtrer par groupe, pays, secteur, statut ; accéder au rapport contenant l’alerte.
- **Note** : jamais d’URL .onion dans l’interface, seulement un indicateur “URL disponible dans les logs sécurisés”.

### 6.5 Administration

Accessible uniquement Admin.

Sections :

- **Utilisateurs & rôles** :
  - création / suppression d’utilisateurs (email + mot de passe + rôle),
  - reset mot de passe par email, gestion MFA (activation, reset),
  - politique de mot de passe : Admin min 16 caractères, Viewer min 12 caractères, rotation tous les 6 mois avec blocage si non renouvelé.

- **Clés API & intégrations** :
  - formulaire pour configurer : TARGET_DOMAIN, HIBP_API_KEY, GITHUB_TOKEN, URLSCAN_API_KEY, OTX_API_KEY, LEAKCHECK_API_KEY, DEHASHED_API_KEY, etc.,
  - paramètres RansomLook (URL locale vs SaaS + API key si SaaS),
  - indicateur visuel si la clé est présente (bool), sans jamais la montrer en clair,
  - bouton “Tester cette source” (ping de santé).

- **Configuration SMTP / mail** :
  - host, port, TLS/SSL, user/password, from, reply-to,
  - bouton “Envoyer un mail de test”.

- **Scheduling** :
  - activation/désactivation du cron hebdomadaire,
  - expression cron configurable (avec validation),
  - affichage du prochain run prévu.

- **Audit trail** :
  - liste des actions admins : login, modification clé, changement de rôle, relance scan, export de rapport, etc.,
  - filtrage par user / type d’action.

### 6.6 Page “Changelog / Updates”

- Liste des grandes évolutions de la plateforme (version, date, résumé).
- Accessible depuis le bas du menu.

## 7. WebUI — i18n

- Langues : **EN** par défaut, **FR**.
- Bouton de sélection de langue dans le header (icône globe + abréviation).
- Stockage de la préférence en cookie/localStorage, fallback sur header Accept-Language.
- Textes externalisés (fichiers `en.json`, `fr.json` côté frontend).

## 8. CLI d’administration (ligne de commande)

> CLI d’**administration / intégration** utilisable dans le conteneur backend. Elle vise les ops/dev, pas les utilisateurs finaux.

### 8.1 Objectifs CLI

- Fournir des commandes scripts-friendly pour :
  - déclencher un scan complet ou spécifique,
  - vérifier la santé des sources (dont RansomLook),
  - lister les derniers scans et leur statut,
  - générer un rapport (PDF) à partir de l’ID de scan.

### 8.2 Stack CLI

- Implémentation Python (Typer ou Click) dans `backend/app/main_cli.py` par exemple.
- Execution typique :

```bash
# Dans le conteneur backend
docker compose exec backend python -m app.main_cli scan --full
```

### 8.3 Commandes minimales

- `scan full`
  - lance un scan complet avec toutes les sources activées.
  - options : `--async` (retour immédiat / job en arrière-plan), `--tag <label>`.

- `scan tool --name <source>`
  - lance un scan limité à une source (ex. `hibp`, `github`, `ransomlook`).

- `ransomlook health`
  - vérifie la santé de l’instance RansomLook (locale ou SaaS).

- `ransomlook check --domain <domain>`
  - force une vérification du domaine sur RansomLook.

- `report generate --scan-id <id> --format pdf`
  - génère un rapport PDF pour un scan existant, stocké dans `reports/`.

- `scans list --limit N`
  - liste les N derniers scans (id, date, durée, sévérité globale).

## 9. Sécurité & conformité

- **Web** :
  - CSRF sur formulaires.
  - Rate limiting sur `/auth/login`, `/scan/*`, `/reports/export`.
  - Validation stricte des entrées (Pydantic côté backend).

- **Mots de passe et MFA** :
  - politiques décrites plus haut (longueur, rotation, blocage),
  - secret TOTP stocké de manière chiffrée (ex. Fernet/Key Management).

- **Données et RGPD** :
  - aucune donnée brute sensible (mot de passe, hash, clé API, URL .onion) en base,
  - uniquement des indicateurs : booléens (has_password, has_hash…), méta-données de fuites, etc.,
  - RansomLook : données déjà publiques, mais on empêche l’exposition directe des URL .onion (seuls les admin avancés peuvent les voir dans des logs sécurisés hors WebUI).

## 10. Déploiement & configuration

- **Fichier `.env` unique** pour :
  - paramètres WebUI (JWT, admin initial, DB, Redis),
  - clés API OSINT,
  - configuration RansomLook (mode local vs SaaS + URL + API key).

- **docker-compose** :
  - un `docker compose up -d` doit démarrer la stack WebUI complète, RansomLook inclus (mode local),
  - en mode SaaS RansomLook, aucun conteneur RansomLook n’est lancé, seul `RANSOMLOOK_SAAS_API_URL` + `RANSOMLOOK_SAAS_API_KEY` sont utilisés.
