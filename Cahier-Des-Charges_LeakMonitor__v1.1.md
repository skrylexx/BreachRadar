# Cahier des Charges Technique — LeakMonitor
## Système de détection de fuites de données ciblé sur un domaine

---

> **Version** : 1.1  
> **Statut** : Draft — Mise à jour : intégration complète RansomLook  
> **Cadre** : Usage légal — surveillance de son propre domaine (OSINT défensif)

---

## Table des matières

1. [Contexte et état de l'art](#1-contexte-et-état-de-lart)
2. [Cadre légal](#2-cadre-légal)
3. [Périmètre du projet](#3-périmètre-du-projet)
4. [Architecture générale](#4-architecture-générale)
5. [Stack technique](#5-stack-technique)
6. [Sources de données](#6-sources-de-données)
7. [RansomLook — Déploiement et intégration complète](#7-ransomlook--déploiement-et-intégration-complète)
8. [Modules fonctionnels](#8-modules-fonctionnels)
9. [Modèle de rapport](#9-modèle-de-rapport)
10. [Sécurité & vie privée by design](#10-sécurité--vie-privée-by-design)
11. [Structure du projet et README](#11-structure-du-projet-et-readme)
12. [Configuration des clés API et services](#12-configuration-des-clés-api-et-services)
13. [Plan de tests](#13-plan-de-tests)
14. [Roadmap et évolutions](#14-roadmap-et-évolutions)

---

## 1. Contexte et état de l'art

### 1.1 Comment fonctionnent HaveIBeenPwned, OutPost24 et leurs pairs ?

Ces services reposent sur un concept commun : **la consolidation de bases de données de fuites** (appelées *breaches* ou *combolists*) issues de diverses sources, puis leur indexation pour permettre des requêtes.

#### Cycle de vie d'une donnée leakée chez ces services

```
Incident de sécurité (breach)
        │
        ▼
Diffusion underground (forums, paste sites, dark web)
        │
        ▼
Collecte par les équipes / crawlers / sources partenaires
        │
        ▼
Normalisation & déduplication
        │
        ▼
Hachage des mots de passe (SHA-1 / k-anonymity pour HIBP)
        │
        ▼
Indexation dans une base de données (Elasticsearch / SQL)
        │
        ▼
Exposition via API REST
```

**HaveIBeenPwned (HIBP)** — Troy Hunt (Microsoft MVP) :
- Indexe + de 14 milliards de comptes issus de centaines de fuites.
- Utilise le modèle **k-anonymity** pour l'API de mots de passe : le client envoie les 5 premiers caractères du SHA-1, le serveur renvoie tous les hashs correspondants ; le client filtre localement. Aucun mot de passe clair ne transite.
- Sources : soumissions communautaires, partenariats (FBI, NCA UK), scrapers dédiés.
- API payante pour les domaines (Domain Search), gratuite pour les emails individuels.

**OutPost24 / SpyCloud / Flare.io** — Solutions B2B :
- Déploient des agents automatisés sur des marchés underground fermés (accès par invitation).
- Achètent ou échangent des dumps avec des partenaires dans une zone grise légale très encadrée.
- Proposent des alertes en temps réel et de l'enrichissement (corrélation avec des identités Active Directory).

**LeakCheck, Snusbase, IntelX** :
- Agrégateurs de combolists publics ou semi-publics.
- Certains opèrent dans des zones légales grises ; leur légitimité varie selon la juridiction.

### 1.2 Sur quoi se basent-ils concrètement ?

| Type de source | Exemples | Accessibilité |
|---|---|---|
| Paste sites | Pastebin, Ghostbin, Rentry | Publique, API disponible |
| Forums underground | BreachForums, XSS.is, Nulled | Privée/invitation |
| Dark Web markets | Marchés Tor | Très restreint, légalement risqué |
| Dumps publics collectifs | Have I Been Pwned dataset | Publique (partagé par Troy Hunt) |
| Sources gouvernementales | FBI IC3, CISA Known Breaches | Publique, partielle |
| Recherche académique | LabsLeaked, academic papers | Publique |
| APIs OSINT | Dehashed, LeakCheck, IntelX | Payante |
| GitHub / GitLab / Bitbucket | Repos publics, gists | Publique, API officielle |
| S3 Buckets mal configurés | Recherche via grayhat, buckets.grayhatwarfare.com | Publique |
| Telegram channels | Canaux de partage de leaks | Publique/restreint |
| **Sites "Name & Shame" ransomware** | **LockBit, BlackCat, Cl0p, Play… (via RansomLook)** | **Publique agrégée, auto-hébergeable** |

### 1.3 Est-ce du scraping/crawling ? Est-ce légal ?

**Techniquement** : oui, en grande partie. Ces systèmes combinent :
- **Web scraping** (extraction de contenu depuis des pages HTML).
- **API crawling** (interrogation d'APIs publiques ou privées).
- **Monitoring de flux** (RSS, webhooks, canaux Telegram).
- **Achat de données** (pour les acteurs B2B).

**Légalement** :
- En France et en UE, scraper des données **personnelles** sans consentement viole le RGPD (Article 6 — base légale du traitement). Cependant, la **détection de fuites dans un but de sécurité** bénéficie de la base légale "intérêt légitime" (Article 6.1.f) **si** le traitement est proportionné et limité.
- La **LCEN** et le **Code Pénal (Art. 323-1 sq.)** interdisent l'accès non autorisé à des systèmes informatiques — scraper un forum underground "fermé" peut être illégal.
- La directive NIS2 (transposée en France fin 2024) **encourage** la mise en place de tels systèmes de veille pour les opérateurs d'importance vitale.
- **Notre approche** : se limiter strictement aux **sources publiques** et aux **APIs légitimes**, ne stocker aucune donnée, opérer uniquement sur son propre domaine.

---

## 2. Cadre légal

### 2.1 Principes directeurs (RGPD / droit français)

| Principe | Application dans ce projet |
|---|---|
| **Minimisation des données** | Aucune donnée personnelle stockée ; traitement en mémoire uniquement |
| **Finalité déterminée** | Détection de compromission sur le domaine propre de l'opérateur |
| **Limitation de conservation** | Zéro rétention — seul le rapport final est conservé (sans données sensibles) |
| **Légitimité du traitement** | Intérêt légitime (Art. 6.1.f RGPD) + sécurité des SI |
| **Intégrité & confidentialité** | Rapport masqué, no-log, chiffrement local |

### 2.2 Ce que ce projet NE fait PAS

- Il ne stocke pas d'adresses email, mots de passe, hashs ou données personnelles tierces.
- Il n'accède pas à des systèmes non autorisés (forums privés, dark web).
- Il ne collecte pas de données sur des domaines qui ne vous appartiennent pas.
- Il ne revend pas, ne partage pas, ne publie pas les données découvertes.

### 2.3 Recommandations

- Documenter votre légitimité à surveiller le domaine cible (inscription WHOIS, attestation de propriété).
- Notifier vos utilisateurs dans votre politique de sécurité (Privacy Policy / PSSI).
- Si vous détectez des fuites impliquant des tiers, notifier la CNIL selon l'Article 33 RGPD.

---

## 3. Périmètre du projet

### 3.1 Objectif principal

Créer un outil CLI + scheduler permettant de **détecter si des données appartenant à un domaine donné (`@mondomaine.fr`) ont été compromises**, en agrégeant plusieurs sources publiques et APIs légitimes, et en produisant un **rapport neutre sans donnée sensible exposée**.

Ce projet intègre deux dimensions complémentaires :

**Dimension 1 — Détection de fuites passées (backward-looking)**
Recherche si des emails du domaine ont déjà été compromis dans des breaches connues (HIBP, Dehashed, LeakCheck…). La donnée est déjà dans la nature.

**Dimension 2 — Early Warning System ransomware (forward-looking) via RansomLook**
Détecte si le domaine ou l'organisation apparaît sur un site "Name & Shame" de groupe de ransomware **avant même que les données ne soient publiées**. C'est un indicateur de compromission actif (IoC) de niveau catastrophique : cela signifie qu'une exfiltration massive est en cours ou vient de se terminer, et que le groupe extorque actuellement l'organisation. La fenêtre de réaction (entre la publication sur le site du groupe et la mise en ligne publique des données) est typiquement de 5 à 30 jours.

> **Concrètement** : on ne cherche plus seulement si `user@domain.fr` est dans une base de données leakée, mais si `domain.fr` est listé comme victime d'un groupe (LockBit, BlackCat/ALPHV, Cl0p, Play, etc.) sur son portail d'extorsion.

### 3.2 Ce qui est dans le scope

- Requêtes sur APIs OSINT légitimes (payantes et gratuites).
- Monitoring de sources publiques (Pastebin-like, GitHub, etc.).
- Parsing de dumps publics légitimement redistribués (HIBP dataset).
- Génération d'un rapport structuré masquant les informations sensibles.
- Orchestration planifiée (cron / scheduler).

### 3.3 Ce qui est hors scope

- Accès aux forums underground, dark web, marchés Tor.
- Bruteforce, phishing ou toute technique active d'attaque.
- Surveillance de domaines ne vous appartenant pas.
- Stockage long terme de données personnelles.

---

## 4. Architecture générale

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                  LeakMonitor                                         │
│                                                                                      │
│  ┌───────────────┐     ┌───────────────┐     ┌──────────────────┐                   │
│  │  Scheduler    │────▶│  Orchestrator │────▶│  Report Engine   │                   │
│  │  (APScheduler │     │  (Async Core) │     │  (Jinja2 + JSON) │                   │
│  │   / Cron)     │     │               │     │                  │                   │
│  └───────────────┘     └──────┬────────┘     └──────────────────┘                   │
│                               │                                                      │
│         ┌─────────────────────┼──────────────────────┐                              │
│         ▼                     ▼                      ▼                              │
│  ┌─────────────┐    ┌──────────────────┐   ┌─────────────────────────────────────┐  │
│  │ API Clients │    │  Feed Monitor    │   │  RansomLook Client                  │  │
│  │             │    │                  │   │  (HTTP → localhost:8888)            │  │
│  │ - HIBP API  │    │ - Pastebin       │   │                                     │  │
│  │ - IntelX    │    │ - GitHub / GL    │   │  ┌──────────────────────────────┐   │  │
│  │ - LeakCheck │    │ - Telegram       │   │  │  Docker : ransomlook         │   │  │
│  │ - Dehashed  │    │ - RSS/CERT/ANSSI │   │  │  ├── app  (Python/Flask)     │   │  │
│  │ - URLScan   │    │                  │   │  │  ├── redis (stockage)         │   │  │
│  │ - OTX       │    └──────────────────┘   │  │  └── tor  (accès .onion)     │   │  │
│  └─────────────┘                           │  └──────────────────────────────┘   │  │
│                                            │  Surveille 100+ groupes ransomware  │  │
│                                            │  et leurs portails d'extorsion      │  │
│                                            └─────────────────────────────────────┘  │
│                                                                                      │
│  ┌───────────────────────────────────────────────────────────┐                      │
│  │               Anonymizer / Sanitizer Layer                │                      │
│  │  (Masquage des mots de passe, hashs, clés API, tokens)    │                      │
│  │  Note : les données RansomLook (nom victime, description) │                      │
│  │  sont publiques par nature — elles ne sont PAS masquées   │                      │
│  └───────────────────────────────────────────────────────────┘                      │
│                                                                                      │
│  ┌──────────────┐                                                                    │
│  │  No-Storage  │  Aucune donnée personnelle persistée                               │
│  │  Policy      │  (traitement en mémoire uniquement)                                │
│  └──────────────┘                                                                    │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Flux de données

```
1.  Scheduler déclenche une analyse (manuelle ou planifiée)
2.  L'Orchestrator charge la config (domaine cible, sources activées, clés API)
3a. Chaque module API client est appelé en parallèle (asyncio)
3b. Le Feed Monitor interroge les flux en temps réel
3c. Le RansomLook Client interroge l'instance Docker locale
         └── Si le domaine est trouvé : ALERTE CRITIQUE immédiate
             (notification déclenchée sans attendre la fin du scan complet)
4.  Les résultats bruts transitent par le Sanitizer (masquage immédiat)
         └── Exception RansomLook : données déjà publiques, pas de masquage
5.  L'Orchestrator déduplique et agrège les findings
         └── Un finding RansomLook élève automatiquement la sévérité globale à CRITICAL
6.  Le Report Engine génère le rapport final (JSON + Markdown/HTML)
         └── Section dédiée "Alertes Ransomware" en tête de rapport si applicable
7.  Les données brutes sont purgées de la mémoire
8.  (Optionnel) Notification par email/webhook
```

---

## 5. Stack technique

### 5.1 Langage principal

**Python 3.12+** — justification :
- Ecosystème OSINT le plus riche (theHarvester, holehe, etc.).
- `asyncio` natif pour les requêtes parallèles.
- Bibliothèques de hachage, chiffrement, HTTP de premier ordre.
- Déploiement simple, CI/CD mature.

### 5.2 Dépendances principales

```toml
# pyproject.toml

[tool.poetry.dependencies]
python = "^3.12"

# HTTP & Async
httpx = "^0.27"           # Client HTTP async, meilleur que aiohttp pour REST
aiohttp = "^3.9"          # Fallback pour certains cas complexes
tenacity = "^8.3"         # Retry avec backoff exponentiel

# Parsing & données
pydantic = "^2.7"         # Validation et sérialisation des modèles
pydantic-settings = "^2.3"
orjson = "^3.10"          # JSON ultra-rapide

# Sécurité & cryptographie
cryptography = "^42"      # Hachage, chiffrement
passlib = "^1.7"          # Utilitaires hash (bcrypt, sha512, etc.)
python-dotenv = "^1.0"    # Gestion des variables d'environnement

# Scheduling
apscheduler = "^3.10"     # Scheduler robuste
croniter = "^2.0"         # Parsing expressions cron

# Rapports
jinja2 = "^3.1"           # Templates de rapport
rich = "^13.7"            # Affichage console coloré et structuré
weasyprint = "^62"        # Export PDF (optionnel)

# Monitoring de flux
feedparser = "^6.0"       # RSS/Atom
telethon = "^1.36"        # Client Telegram (optionnel, pour canaux publics)

# Tests
pytest = "^8.2"
pytest-asyncio = "^0.23"
pytest-cov = "^5.0"
respx = "^0.21"           # Mock httpx

# Qualité de code
ruff = "^0.4"             # Linter + formatter ultra-rapide
mypy = "^1.10"            # Type checking
```

### 5.3 Outils de développement

| Outil | Rôle |
|---|---|
| **uv** | Gestionnaire de paquets et d'environnements ultra-rapide (remplace pip/venv) |
| **Docker + Docker Compose** | Conteneurisation pour déploiement reproductible |
| **GitHub Actions** | CI/CD : lint, tests, build image |
| **Makefile** | Commandes standardisées (make run, make test, make report) |
| **pre-commit** | Hooks git (ruff, mypy, secrets scanner) |

---

## 6. Sources de données

### 6.1 Sources gratuites (priorité haute)

#### 6.1.1 HaveIBeenPwned API v3 — API gratuite (email individuel)
- **URL** : `https://haveibeenpwned.com/api/v3/breachedaccount/{email}`
- **Auth** : Clé API requise pour les recherches email (environ 3,50 USD/mois)
- **Domain search** : Payant (abonnement annuel ~550 USD)
- **Rate limit** : 1 requête / 1500ms par clé
- **Ce qu'on récupère** : Nom du service compromis, date, types de données exposées (PII, passwords, etc.) — **jamais les données elles-mêmes**
- **Intégration** : Module dédié avec respect du rate limiting

```python
# Exemple de structure de réponse HIBP
{
  "Name": "Adobe",
  "BreachDate": "2013-10-04",
  "DataClasses": ["Email addresses", "Password hints", "Passwords", "Usernames"],
  "IsVerified": true,
  "IsSensitive": false
}
```

#### 6.1.2 HIBP Pwned Passwords (gratuit, k-anonymity)
- **URL** : `https://api.pwnedpasswords.com/range/{hash_prefix}`
- **Auth** : Aucune
- **Usage** : Vérifier si un hash de mot de passe figure dans les 847M+ hashs indexés
- **Note** : Ce module ne sera activé que si un hash est transmis — jamais de mot de passe en clair

#### 6.1.3 GitHub / GitLab Public Search
- **URL** : `https://api.github.com/search/code?q={domain}` et `https://gitlab.com/api/v4/search`
- **Auth** : Token GitHub (gratuit, 5000 req/h authentifié vs 60/h anonyme)
- **Usage** : Détecter des credentials hardcodés dans des repos publics (`.env`, `config`, `credentials`)
- **Patterns recherchés** : emails `@mondomaine.fr`, tokens, clés API

#### 6.1.4 Pastebin Scraping API (API dédiée)
- **URL** : `https://scrape.pastebin.com/api_scraping.php`
- **Auth** : Réservé aux comptes Pro Pastebin (~$5/mois)
- **Alternative** : Pwnbin (open source, surveille Pastebin + autres paste sites)
- **Usage** : Détecter des dumps mentionnant le domaine

#### 6.1.5 GreyNoise & Shodan (exposition infrastructure)
- **Shodan** : `https://api.shodan.io/dns/domain/{domain}` — infra exposée
- **GreyNoise** : Enrichissement threat intelligence
- **Auth** : Clé API (tier gratuit disponible)

#### 6.1.6 URLScan.io
- **URL** : `https://urlscan.io/api/v1/search/?q=domain:{domain}`
- **Auth** : Clé API gratuite
- **Usage** : Détecter des pages de phishing imitant votre domaine

#### 6.1.7 AlienVault OTX (Open Threat Exchange)
- **URL** : `https://otx.alienvault.com/api/v1/indicators/domain/{domain}/general`
- **Auth** : Clé API gratuite
- **Usage** : Indicateurs de compromission liés au domaine

#### 6.1.8 Breach.Directory (API partielle gratuite)
- **URL** : `https://breach.directory/api/search?query={email}`
- **Auth** : Clé API (tier gratuit limité)

#### 6.1.9 RansomLook (gratuit, auto-hébergé via Docker — **Fortement recommandé**)

RansomLook est un projet open source qui **agrège et normalise les publications des portails d'extorsion de groupes ransomware** (leurs sites "Name & Shame" sur le dark web et clearnet). Il surveille en continu plus de 100 groupes actifs (LockBit, BlackCat/ALPHV, Cl0p, Play, Akira, RansomHub, etc.) et expose leurs publications via une API REST locale.

> **Pourquoi c'est différent des autres sources** : HIBP et les autres APIs détectent des fuites *passées*. RansomLook détecte une compromission *en cours* — avant même que les données ne soient publiées. C'est la seule source qui donne une chance de réagir pendant la fenêtre d'extorsion.

**Dépôt GitHub** : `https://github.com/RansomLook/RansomLook`  
**Instance publique** : `https://www.ransomlook.io`  
**Auth** : Aucune sur instance locale ; clé API sur l'instance publique (voir section 12.12)  
**Coût** : Gratuit (auto-hébergé) — seuls les coûts d'infrastructure s'appliquent

**Endpoints API utilisés dans LeakMonitor :**

```
# Instance locale sur Docker (port 8888 par défaut)
BASE_URL = http://localhost:8888

GET /api/v1/recent
  → Liste des victimes publiées récemment (toutes groupes confondus)
  → Paramètre optionnel : ?days=7 (derniers N jours)

GET /api/v1/groups
  → Liste de tous les groupes ransomware suivis avec leur statut (actif/inactif)

GET /api/v1/group?name={group_name}
  → Toutes les victimes d'un groupe spécifique
  → Ex : /api/v1/group?name=lockbit3

GET /api/v1/victims
  → Toutes les victimes indexées (pagination recommandée)

GET /api/v1/victim?name={search_term}
  → Recherche par nom de victime / domaine
  → C'est l'endpoint principal utilisé par LeakMonitor

GET /api/v1/stats
  → Statistiques globales (nombre de groupes, victimes, date dernière mise à jour)
```

**Exemple de réponse `/api/v1/victim?name=mondomaine` :**

```json
[
  {
    "post_title": "MonDomaine SA",
    "group_name": "lockbit3",
    "discovered": "2025-04-20T14:32:00Z",
    "published": "2025-04-20T14:32:00Z",
    "post_url": "http://lockbit3abc[.]onion/post/abc123",
    "description": "500GB of internal data, including SQL databases and employee emails.",
    "website": "mondomaine.fr",
    "country": "France",
    "activity": "Technology",
    "claim_size": "500GB",
    "infostealer": false,
    "added": "2025-04-20T15:00:00Z"
  }
]
```

**Stratégie de matching dans LeakMonitor :**

La recherche ne se fait pas uniquement sur le nom de domaine exact — l'organisation peut être listée sous son nom commercial, ses filiales, ou son acronyme. LeakMonitor applique une stratégie de matching en cascade :

```python
# Termes de recherche configurables dans .env
RANSOMLOOK_SEARCH_TERMS=mondomaine.fr,MonDomaine,MDomaine,MD Group
# → Chaque terme génère une requête GET /api/v1/victim?name={term}
# → Les résultats sont fusionnés et dédupliqués
```

### 6.2 Sources payantes recommandées

| Service | Prix indicatif | Valeur ajoutée |
|---|---|---|
| **HaveIBeenPwned Domain Search** | ~550 USD/an | Scan complet de domaine, toutes les breaches |
| **IntelX (Intelligence X)** | ~100–500 EUR/mois | Indexation dark web, Tor, I2P, paste sites |
| **LeakCheck.io** | ~10–50 USD/mois | Base de données de leaks consolidée, API REST |
| **Dehashed** | ~5–180 USD/mois | 15+ milliards de records, recherche email/domaine |
| **Flare.io** | Sur devis | Monitoring dark web professionnel |
| **SpyCloud** | Sur devis | Focus sur le credential stuffing B2B |
| **Constella Intelligence** | Sur devis | Enrichissement identités, couplage avec AML |

### 6.3 Sources open data (datasets)

| Dataset | Format | Taille | Source |
|---|---|---|---|
| HIBP Pwned Passwords | SHA-1, texte ordonné | ~50 GB | haveibeenpwned.com/Passwords |
| Collection #1 (historique) | Texte, combolist | Public mais sensible | Archive.org |
| BreachCompilation | Texte | 41 GB | Redistribué légalement dans cadre recherche |

> **Note** : L'utilisation locale du dataset HIBP Pwned Passwords est explicitement autorisée par Troy Hunt pour un usage défensif. Les autres datasets doivent être évalués au cas par cas sur le plan légal.

### 6.4 Monitoring de canaux publics

| Source | Méthode | Notes |
|---|---|---|
| **Telegram (canaux publics)** | Telethon API | Canaux publics uniquement, pas de groupes privés |
| **RSS feeds** | feedparser | Blogs sécurité, CERT, CISA, ANSSI |
| **Twitter/X** | API v2 (Basic) | Veille sur mots-clés (domaine, breach, leak) |
| **Reddit** | API officielle (gratuite) | r/netsec, r/privacy, etc. |

---

## 7. RansomLook — Déploiement et intégration complète

### 7.1 Qu'est-ce que RansomLook ?

RansomLook est un **agrégateur open source de sites "Name & Shame" de groupes ransomware**. Ces groupes, lorsqu'ils chiffrent les données d'une organisation et que la rançon n'est pas payée, publient le nom de leur victime sur un portail web (souvent en .onion sur Tor, parfois aussi sur le clearnet) pour exercer une pression supplémentaire. RansomLook scrape automatiquement ces portails et expose les données via une API REST normalisée.

**Ce que RansomLook surveille :**
- 100+ groupes ransomware actifs (LockBit, BlackCat/ALPHV, Cl0p, Play, Akira, RansomHub, Medusa, etc.)
- Les portails .onion (via Tor intégré) **et** les miroirs clearnet
- Les nouvelles publications en quasi temps réel (refresh configurable, typiquement toutes les heures)
- Les métadonnées associées : date, taille des données revendiquées, secteur, pays, description

**Ce que RansomLook ne fait PAS :**
- Il ne télécharge pas les données volées
- Il n'accède pas aux espaces privés des portails (nécessitant un paiement ou une clé)
- Il ne déchiffre aucune donnée

> **Statut légal** : RansomLook consulte des pages web publiquement accessibles (même sur Tor) pour collecter des informations que les groupes ransomware ont délibérément rendues publiques. Cette pratique est analogue à la surveillance de presse et est légale dans le cadre d'un usage défensif, notamment en France sous le régime de l'intérêt légitime (RGPD Art. 6.1.f) et dans le cadre de la LPM / NIS2.

---

### 7.2 Architecture Docker de RansomLook

RansomLook est composé de trois services Docker :

```
┌─────────────────────────────────────────────────────────────────┐
│               Stack Docker RansomLook                           │
│                                                                 │
│  ┌─────────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  ransomlook-app │    │    redis     │    │      tor      │  │
│  │  (Python/Flask) │◄──▶│  (stockage   │    │  (accès aux   │  │
│  │  Port: 8888     │    │   des        │◄───│  sites .onion)│  │
│  │                 │    │   données)   │    │               │  │
│  │  - API REST     │    │  Port: 6379  │    │  Port: 9050   │  │
│  │  - Scheduler    │    └──────────────┘    └───────────────┘  │
│  │    interne      │                                           │
│  └─────────────────┘                                           │
│           ▲                                                     │
│           │ HTTP REST                                           │
│  LeakMonitor (Python)                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

### 7.3 Fichier `docker-compose.yml` complet du projet

Le `docker-compose.yml` de LeakMonitor intègre RansomLook comme service dépendant :

```yaml
# docker-compose.yml
version: "3.9"

services:

  # ─────────────────────────────────────────
  # RansomLook — stack complète auto-hébergée
  # ─────────────────────────────────────────

  ransomlook-redis:
    image: redis:7-alpine
    container_name: ransomlook-redis
    restart: unless-stopped
    volumes:
      - ransomlook_redis_data:/data
    networks:
      - ransomlook_net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ransomlook-tor:
    image: dperson/torproxy:latest
    container_name: ransomlook-tor
    restart: unless-stopped
    networks:
      - ransomlook_net
    environment:
      - TOR_MaxCircuitDirtiness=600
    healthcheck:
      test: ["CMD", "curl", "--socks5", "localhost:9050", "https://check.torproject.org/api/ip"]
      interval: 30s
      timeout: 15s
      retries: 5

  ransomlook-app:
    image: ghcr.io/ransomlook/ransomlook:latest
    container_name: ransomlook-app
    restart: unless-stopped
    depends_on:
      ransomlook-redis:
        condition: service_healthy
      ransomlook-tor:
        condition: service_healthy
    ports:
      - "127.0.0.1:8888:8888"   # Exposé uniquement en localhost — jamais en 0.0.0.0
    networks:
      - ransomlook_net
    environment:
      - REDIS_HOST=ransomlook-redis
      - REDIS_PORT=6379
      - TOR_PROXY=socks5://ransomlook-tor:9050
      - REFRESH_INTERVAL=3600     # Rafraîchissement toutes les heures
      - LOG_LEVEL=WARNING
    volumes:
      - ransomlook_app_data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/api/v1/stats"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s           # Laisser le temps au premier scrape

  # ─────────────────────────────────────────
  # LeakMonitor — application principale
  # ─────────────────────────────────────────

  leakmonitor:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: leakmonitor
    restart: unless-stopped
    depends_on:
      ransomlook-app:
        condition: service_healthy
    env_file:
      - .env
    environment:
      - RANSOMLOOK_URL=http://ransomlook-app:8888   # Communication inter-container
    volumes:
      - ./reports:/app/reports
    networks:
      - ransomlook_net

volumes:
  ransomlook_redis_data:
  ransomlook_app_data:

networks:
  ransomlook_net:
    driver: bridge
```

> **Note de sécurité** : L'API RansomLook est liée à `127.0.0.1:8888` uniquement (pas `0.0.0.0`). Elle ne doit pas être exposée sur Internet — elle contient des informations sur des victimes de ransomware et n'a pas de système d'authentification sur les endpoints de lecture.

---

### 7.4 Premier démarrage et initialisation

```bash
# 1. Démarrer la stack RansomLook uniquement (pour le premier peuplement des données)
docker-compose up ransomlook-redis ransomlook-tor ransomlook-app -d

# 2. Vérifier que les services sont sains
docker-compose ps

# 3. Attendre le premier cycle de scraping (peut prendre 10-30 minutes)
#    Surveiller les logs :
docker-compose logs -f ransomlook-app

# 4. Vérifier que l'API répond et que des données sont présentes
curl http://localhost:8888/api/v1/stats
# Attendu : {"groups": 120, "posts": 14500, "last_update": "2025-..."}

# 5. Tester la recherche par domaine
curl "http://localhost:8888/api/v1/victim?name=mondomaine.fr"
# Attendu : [] (tableau vide si votre domaine n'est pas compromis — c'est le scénario souhaité)

# 6. Démarrer la stack complète (LeakMonitor + RansomLook)
docker-compose up -d
```

---

### 7.5 Modèle de données RansomLook (Pydantic)

Ces modèles sont spécifiques à RansomLook et distincts du modèle `LeakFinding` standard (les données ransomware sont publiques, pas de sanitisation) :

```python
# leakmonitor/models/ransom.py

from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class RansomStatus(str, Enum):
    LISTED = "LISTED"           # Victime listée, données pas encore publiées
    PUBLISHED = "PUBLISHED"     # Données publiées / téléchargeables
    REMOVED = "REMOVED"         # Publication supprimée (rançon payée ?)
    UNKNOWN = "UNKNOWN"

class RansomFinding(BaseModel):
    """
    Résultat d'une correspondance RansomLook.
    Ces données sont publiques (publiées par le groupe ransomware lui-même)
    et ne nécessitent pas de sanitisation.
    """
    source: str = "ransomlook"
    group_name: str                  # Ex: "lockbit3", "blackcat", "play"
    group_display_name: str          # Ex: "LockBit 3.0", "BlackCat/ALPHV"
    victim_name: str                 # Nom tel qu'affiché sur le portail du groupe
    victim_website: str | None       # Domaine de la victime si disponible
    discovered_at: datetime          # Date de découverte par RansomLook
    published_at: datetime | None    # Date de publication sur le portail
    description: str | None          # Description publique (SANS données réelles)
    country: str | None              # Pays de la victime
    activity: str | None             # Secteur d'activité
    claim_size: str | None           # Taille revendiquée ("500GB", "2TB")
    status: RansomStatus
    portal_url: str | None           # URL .onion (affichée masquée dans le rapport)
    search_term_matched: str         # Terme de recherche qui a matché
    severity: str = "CRITICAL"       # Toujours CRITICAL — pas de négociation

class RansomStats(BaseModel):
    """Statistiques de l'instance RansomLook locale."""
    groups_tracked: int
    total_posts: int
    last_update: datetime | None
    instance_url: str
    is_healthy: bool
```

---

### 7.6 Client Python `ransomlook.py`

```python
# leakmonitor/clients/ransomlook.py

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from leakmonitor.clients.base import BaseLeakClient
from leakmonitor.models.ransom import RansomFinding, RansomStats, RansomStatus
from leakmonitor.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Mapping des noms de groupes techniques → noms affichables
GROUP_DISPLAY_NAMES = {
    "lockbit3": "LockBit 3.0",
    "blackcat": "BlackCat / ALPHV",
    "clop": "Cl0p",
    "play": "Play",
    "akira": "Akira",
    "ransomhub": "RansomHub",
    "medusa": "Medusa",
    "bianlian": "BianLian",
    "8base": "8Base",
    # ... liste complète dans config/group_names.yaml
}

class RansomLookClient(BaseLeakClient):
    name = "ransomlook"
    rate_limit_delay = 0.5  # Requêtes locales — pas de rate limit strict

    def __init__(self):
        self.base_url = settings.ransomlook_url.rstrip("/")
        self.search_terms = settings.ransomlook_search_terms  # list[str]
        self.timeout = httpx.Timeout(30.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _get(self, path: str, params: dict = None) -> dict | list:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}", params=params)
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> RansomStats:
        """Vérifie que l'instance RansomLook est opérationnelle."""
        try:
            data = await self._get("/api/v1/stats")
            return RansomStats(
                groups_tracked=data.get("groups", 0),
                total_posts=data.get("posts", 0),
                last_update=data.get("last_update"),
                instance_url=self.base_url,
                is_healthy=True,
            )
        except Exception as e:
            logger.error(f"RansomLook instance non joignable : {e}")
            return RansomStats(
                groups_tracked=0, total_posts=0, last_update=None,
                instance_url=self.base_url, is_healthy=False
            )

    async def check_domain(self, domain: str) -> list[RansomFinding]:
        """
        Recherche le domaine ET tous les termes configurés dans RANSOMLOOK_SEARCH_TERMS.
        Déduplique les résultats par (group_name, victim_name, published_at).
        """
        findings: list[RansomFinding] = []
        seen: set[tuple] = set()

        # On cherche sur tous les termes configurés (domaine + noms d'organisation)
        search_terms = list({domain, *self.search_terms})

        for term in search_terms:
            try:
                results = await self._get("/api/v1/victim", params={"name": term})
                for item in results:
                    dedup_key = (
                        item.get("group_name"),
                        item.get("post_title"),
                        item.get("published"),
                    )
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    group_name = item.get("group_name", "unknown")
                    finding = RansomFinding(
                        group_name=group_name,
                        group_display_name=GROUP_DISPLAY_NAMES.get(
                            group_name, group_name.title()
                        ),
                        victim_name=item.get("post_title", ""),
                        victim_website=item.get("website"),
                        discovered_at=item.get("added") or item.get("discovered"),
                        published_at=item.get("published"),
                        description=item.get("description"),
                        country=item.get("country"),
                        activity=item.get("activity"),
                        claim_size=item.get("claim_size"),
                        status=RansomStatus.LISTED,
                        portal_url=item.get("post_url"),  # Stocké mais masqué en rapport
                        search_term_matched=term,
                    )
                    findings.append(finding)
                    logger.critical(
                        f"🚨 RANSOMWARE ALERT : {domain} trouvé sur portail {group_name} "
                        f"(terme matché : '{term}')"
                    )

            except Exception as e:
                logger.error(f"Erreur RansomLook pour terme '{term}' : {e}")

        return findings

    async def get_recent_victims(self, days: int = 7) -> list[dict]:
        """Retourne les victimes récentes pour enrichissement de contexte."""
        return await self._get("/api/v1/recent", params={"days": days})

    # check_email n'est pas applicable pour RansomLook (recherche par organisation)
    async def check_email(self, email: str) -> list[RansomFinding]:
        return []
```

---

## 8. Modules fonctionnels

### 8.1 Configuration Manager

```
config/
├── settings.py          # Pydantic Settings — lecture .env + validation
├── sources.yaml         # Activation/désactivation de chaque source
├── group_names.yaml     # Mapping technique → affichable des groupes ransomware
└── templates/
    └── report.html.j2   # Template Jinja2 du rapport
```

**Fichier `.env` :**
```dotenv
# Domaine cible (IMMUABLE dans ce projet)
TARGET_DOMAIN=mondomaine.fr

# Clés API (voir Section 12 pour obtenir chacune)
HIBP_API_KEY=
GITHUB_TOKEN=
GITLAB_TOKEN=
INTELX_API_KEY=
LEAKCHECK_API_KEY=
DEHASHED_API_KEY=
DEHASHED_EMAIL=
SHODAN_API_KEY=
URLSCAN_API_KEY=
OTX_API_KEY=
TELEGRAM_API_ID=
TELEGRAM_API_HASH=

# ─── RansomLook ─────────────────────────────────────────────────
# URL de l'instance Docker locale (ne pas modifier si docker-compose standard)
RANSOMLOOK_URL=http://localhost:8888

# Termes de recherche : domaine + noms alternatifs de l'organisation
# Séparés par des virgules — le domaine cible est toujours ajouté automatiquement
RANSOMLOOK_SEARCH_TERMS=MonDomaine,Mon Domaine SA,MDomaine

# Notification immédiate si le domaine est trouvé sur RansomLook
# (indépendamment du scheduler normal)
RANSOMLOOK_ALERT_EMAIL=security@mondomaine.fr
RANSOMLOOK_ALERT_WEBHOOK=
# ────────────────────────────────────────────────────────────────

# Configuration rapport
REPORT_OUTPUT_DIR=./reports
REPORT_FORMAT=markdown,json   # markdown | json | html | pdf

# Scheduling
SCHEDULE_ENABLED=false
SCHEDULE_CRON=0 8 * * 1        # Tous les lundis à 8h

# Proxy (optionnel, pour les requêtes sensibles)
HTTP_PROXY=
HTTPS_PROXY=
```

### 8.2 Domain Email Resolver

Avant toute recherche, ce module tente de reconstituer la **liste des adresses connues** du domaine via :

1. **Scraping public** : LinkedIn (via proxycurl ou phantombuster), pages "contact" du site.
2. **MX record analysis** : Vérification que le domaine a bien des MX records (preuve de légitimité mail).
3. **TheHarvester** : Outil OSINT open source, recherche dans Google, Bing, LinkedIn.
4. **hunter.io API** (50 req/mois gratuit) : Découverte d'emails du domaine.
5. **HIBP Domain Search** (si clé disponible) : Retourne directement la liste des emails leakés.

```python
# Interface du module
class DomainEmailResolver:
    async def resolve(self, domain: str) -> list[str]:
        """
        Retourne une liste d'adresses email appartenant au domaine,
        découvertes via sources OSINT publiques.
        """
```

### 8.3 API Clients (un par source)

Chaque client est une classe async héritant d'une base commune :

```python
class BaseLeakClient(ABC):
    name: str
    rate_limit_delay: float  # secondes entre requêtes
    
    @abstractmethod
    async def check_email(self, email: str) -> list[LeakFinding]: ...
    
    @abstractmethod
    async def check_domain(self, domain: str) -> list[LeakFinding]: ...
```

**Modèle de Finding (Pydantic) :**

```python
class LeakFinding(BaseModel):
    source: str                          # Nom de la source
    email: str                           # Email concerné
    breach_name: str                     # Nom de la fuite (ex: "Adobe 2013")
    breach_date: date | None             # Date estimée de la fuite
    data_classes: list[str]              # Types de données (pas les données elles-mêmes)
    has_password: bool                   # Booléen : un mot de passe était présent
    has_hash: bool                       # Booléen : un hash était présent  
    has_api_key: bool                    # Booléen : une clé API était présente
    has_plaintext_credential: bool       # Booléen : credential en clair détecté
    severity: Severity                   # LOW / MEDIUM / HIGH / CRITICAL
    verified: bool                       # La fuite est-elle vérifiée/confirmée ?
    raw_data_sanitized: bool = True      # Toujours True — données brutes purgées
    # NOTE : Aucun champ mot de passe, hash, token, clé API n'existe dans ce modèle
```

### 8.4 Sanitizer Layer

Module central appliqué **immédiatement** après réception de toute réponse d'API :

```python
class DataSanitizer:
    """
    Purge toute donnée sensible des réponses brutes.
    Appelé AVANT toute autre opération sur les données.
    """
    
    SENSITIVE_PATTERNS = [
        r"(?i)password[s]?\s*[:=]\s*\S+",
        r"(?i)passwd\s*[:=]\s*\S+",
        r"(?i)hash\s*[:=]\s*[a-f0-9]{32,}",
        r"[a-f0-9]{32}",                          # MD5
        r"[a-f0-9]{40}",                          # SHA-1
        r"[a-f0-9]{64}",                          # SHA-256
        r"\$2[ayb]\$.{56}",                       # bcrypt
        r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*\S+",
        r"[A-Za-z0-9+/]{40,}={0,2}",             # Base64 potentiel
    ]
    
    def sanitize(self, raw: dict | str) -> SanitizedResult:
        """
        Remplace les valeurs sensibles par des marqueurs.
        Retourne un objet sans données sensibles + des flags booléens.
        """
        # Ex: "password: abc123" → has_password=True, valeur purgée
```

### 8.5 Deduplicator & Aggregator

```python
class ResultAggregator:
    """
    - Déduplique les findings identiques provenant de sources multiples
    - Agrège par email, par breach, par type de données
    - Calcule un score de sévérité global par email
    - Intègre les RansomFinding comme signal de sévérité maximale globale

    ⚠️  RÈGLE CRITIQUE RansomLook :
    Si un RansomFinding est présent (domaine détecté sur portail ransomware),
    la sévérité GLOBALE du rapport est élevée à CRITICAL et une notification
    immédiate est déclenchée, SANS attendre la fin de l'analyse des emails.
    Cela traduit le fait qu'une exfiltration massive est probable ou en cours.
    """

    def aggregate(
        self,
        email_findings: list[LeakFinding],
        ransom_findings: list[RansomFinding],
    ) -> AggregatedReport: ...
```

**Calcul de sévérité pour les findings email :**

| Condition | Niveau |
|---|---|
| Fuite ancienne (> 3 ans), pas de credentials | LOW |
| Email + données PII uniquement | MEDIUM |
| Email + hash de mot de passe présent | HIGH |
| Email + mot de passe en clair ou clé API | CRITICAL |
| Fuite récente (< 6 mois) + tout type | +1 niveau |

**Règles de sévérité RansomLook (sévérité globale du rapport) :**

| Condition RansomLook | Sévérité globale | Action immédiate |
|---|---|---|
| Aucun résultat | — | Aucune |
| Domaine trouvé, données non encore publiées | **CRITICAL** | Alerte immédiate + rapport d'urgence |
| Domaine trouvé, données publiées | **CRITICAL** | Alerte immédiate + rapport d'urgence + CNIL |

### 8.6 Feed Monitor (surveillance continue)

Module asynchrone tournant en arrière-plan pour surveiller :

```python
class FeedMonitor:
    async def monitor_pastebin(self) -> AsyncIterator[LeakFinding]: ...
    async def monitor_github(self) -> AsyncIterator[LeakFinding]: ...
    async def monitor_telegram_public(self) -> AsyncIterator[LeakFinding]: ...
    async def monitor_rss_feeds(self) -> AsyncIterator[LeakFinding]: ...
```

**Patterns détectés dans les flux :**
- Présence du domaine cible dans du texte brut.
- Formats email `*@mondomaine.fr`.
- Noms de services internes (si configurés).
- Fichiers `.env`, `config.yml`, `credentials.json` mentionnant le domaine.

### 8.7 Scheduler

```python
# Utilise APScheduler avec persistance en mémoire (pas de DB)
scheduler = AsyncIOScheduler()

scheduler.add_job(
    run_full_scan,
    CronTrigger.from_crontab(settings.SCHEDULE_CRON),
    id="full_scan",
    max_instances=1,        # Pas de scan concurrent
    coalesce=True,          # Si raté, une seule exécution de rattrapage
    misfire_grace_time=3600
)
```

### 8.8 Notification Engine (optionnel)

```python
class NotificationEngine:
    async def send_email(self, report: FinalReport, recipient: str): ...
    async def send_webhook(self, report: FinalReport, webhook_url: str): ...
    async def send_slack(self, report: FinalReport, channel: str): ...

    async def send_ransom_alert(self, finding: RansomFinding) -> None:
        """
        Notification d'urgence déclenchée IMMÉDIATEMENT à la détection
        d'un RansomFinding, sans attendre la fin du scan complet.
        Contient : groupe ransomware, date de détection, taille revendiquée.
        Ne contient PAS : URL .onion, description complète (peut contenir des PII).
        """
```

**Note** : Les notifications standard ne contiennent que le résumé (nombre de comptes compromis, sévérité max) — jamais de données sensibles. Les alertes RansomLook contiennent le nom du groupe et la date de détection, sans les données de la victime publiées par le groupe.

### 8.9 RansomwareTracker — Module d'orchestration

Ce module orchestre les appels au `RansomLookClient` et gère la logique d'alerte immédiate. Il est distinct du client HTTP (section 7.6) qui lui est délégué.

```python
# leakmonitor/core/ransom_tracker.py

class RansomwareTracker:
    """
    Orchestre la surveillance ransomware via RansomLookClient.
    Gère l'alerte immédiate et l'intégration avec l'Orchestrator principal.
    """

    def __init__(self, client: RansomLookClient, notifier: NotificationEngine):
        self.client = client
        self.notifier = notifier

    async def run(self, domain: str) -> list[RansomFinding]:
        # 1. Vérifier la santé de l'instance RansomLook
        stats = await self.client.check_health()
        if not stats.is_healthy:
            logger.error("Instance RansomLook non disponible — module ignoré")
            return []

        # 2. Recherche multi-termes
        findings = await self.client.check_domain(domain)

        # 3. Alerte immédiate si trouvé (n'attend pas la fin du scan global)
        for finding in findings:
            await self.notifier.send_ransom_alert(finding)

        return findings

    async def get_context(self) -> RansomStats:
        """Retourne les statistiques de l'instance pour inclusion dans le rapport."""
        return await self.client.check_health()
```

---

## 9. Modèle de rapport

### 9.1 Structure JSON (format brut)

```json
{
  "report_metadata": {
    "generated_at": "2025-01-15T08:00:00Z",
    "target_domain": "mondomaine.fr",
    "sources_queried": ["hibp", "leakcheck", "github", "dehashed", "ransomlook"],
    "sources_errors": [],
    "scan_duration_seconds": 42.3,
    "total_emails_checked": 87,
    "total_findings": 12,
    "ransomlook_instance": {
      "url": "http://localhost:8888",
      "is_healthy": true,
      "groups_tracked": 124,
      "total_posts_indexed": 16340,
      "last_update": "2025-01-15T07:45:00Z"
    }
  },
  "ransomware_alerts": {
    "domain_listed": true,
    "alert_count": 1,
    "alerts": [
      {
        "group_name": "lockbit3",
        "group_display_name": "LockBit 3.0",
        "victim_name": "MonDomaine SA",
        "discovered_at": "2025-01-14T14:32:00Z",
        "published_at": "2025-01-14T14:32:00Z",
        "country": "France",
        "activity": "Technology",
        "claim_size": "500GB",
        "status": "LISTED",
        "description_available": true,
        "description": "500GB of internal data, including SQL databases and employee emails.",
        "portal_url_available": true,
        "portal_url": "[URL .onion masquée — disponible dans les logs sécurisés]",
        "search_term_matched": "MonDomaine",
        "severity": "CRITICAL",
        "recommended_actions": [
          "Activer immédiatement le plan de réponse aux incidents (PRI)",
          "Contacter un cabinet de forensics spécialisé ransomware",
          "Notifier la CNIL sous 72h (Art. 33 RGPD)",
          "Évaluer le périmètre de l'exfiltration avec les logs réseau",
          "NE PAS contacter le groupe ransomware sans conseil juridique",
          "Préserver les preuves (logs, artefacts système) pour investigation"
        ]
      }
    ]
  },
  "summary": {
    "global_severity": "CRITICAL",
    "ransomware_detected": true,
    "emails_compromised": 5,
    "emails_clean": 82,
    "severity_breakdown": {
      "CRITICAL": 1,
      "HIGH": 2,
      "MEDIUM": 2,
      "LOW": 0
    },
    "most_common_breaches": ["Adobe 2013", "LinkedIn 2012", "Dropbox 2012"],
    "oldest_breach": "2012-05-01",
    "newest_breach": "2024-03-15"
  },
  "findings": [
    {
      "email": "alice@mondomaine.fr",
      "status": "COMPROMISED",
      "severity": "CRITICAL",
      "breach_count": 3,
      "breaches": [
        {
          "name": "ServiceXYZ",
          "date": "2024-03-15",
          "data_classes": ["Email addresses", "Passwords"],
          "has_password": true,
          "has_hash": false,
          "has_api_key": false,
          "verified": true,
          "source": "hibp",
          "note": "⚠️  Credential sensible détecté — non affiché"
        },
        {
          "name": "Adobe",
          "date": "2013-10-04",
          "data_classes": ["Email addresses", "Password hints"],
          "has_password": false,
          "has_hash": true,
          "has_api_key": false,
          "verified": true,
          "source": "hibp",
          "note": "⚠️  Hash détecté — non affiché"
        }
      ],
      "recommendations": [
        "Forcer le changement de mot de passe immédiatement",
        "Activer l'authentification multi-facteurs",
        "Révoquer les sessions actives",
        "Vérifier les accès liés à ce compte"
      ]
    },
    {
      "email": "bob@mondomaine.fr",
      "status": "CLEAN",
      "severity": null,
      "breach_count": 0,
      "breaches": []
    }
  ],
  "data_integrity": {
    "no_plaintext_passwords_stored": true,
    "no_hashes_stored": true,
    "sanitizer_applied": true,
    "data_purged_after_report": true,
    "ransomlook_data_is_public": true
  }
}
```

### 9.2 Rapport Markdown (format humain)

```markdown
# 🔍 Rapport LeakMonitor — mondomaine.fr
**Généré le** : 15 janvier 2025 à 08:00  
**Sources consultées** : HIBP, LeakCheck, GitHub, Dehashed, RansomLook  
**Durée d'analyse** : 42 secondes

---

## 💀 ALERTE RANSOMWARE — ACTION IMMÉDIATE REQUISE

> ⚠️ **Votre domaine a été détecté sur un portail d'extorsion ransomware.**  
> Cela indique qu'une exfiltration de données est probable ou en cours.  
> Contactez immédiatement votre équipe sécurité et un cabinet de forensics.

| Indicateur | Valeur |
|---|---|
| **Groupe détecté** | LockBit 3.0 |
| **Date de détection** | 14 janvier 2025 à 14:32 |
| **Taille revendiquée** | 500 GB |
| **Statut** | Données non encore publiées (fenêtre de négociation) |
| **Pays** | France |
| **Secteur** | Technology |

**Description publiée par le groupe :**  
*"500GB of internal data, including SQL databases and employee emails."*

**Actions critiques à entreprendre :**
1. 🚨 Activer le Plan de Réponse aux Incidents (PRI) immédiatement
2. 🔒 Isoler les systèmes potentiellement compromis du réseau
3. 🔍 Mandater un cabinet de forensics spécialisé ransomware
4. 📋 Notifier la CNIL dans les 72h (Article 33 RGPD)
5. ⚖️  Ne PAS contacter le groupe sans conseil juridique préalable
6. 📁 Préserver tous les logs et artefacts système pour investigation

---

## 📊 Résumé

| Indicateur | Valeur |
|---|---|
| Emails analysés | 87 |
| **Emails compromis** | **5** |
| Sévérité maximale | 🔴 CRITICAL |
| Alerte ransomware | 🔴 OUI — LockBit 3.0 |
| Fuite la plus récente | 15 mars 2024 |
| Sources en erreur | Aucune |
| RansomLook — Groupes suivis | 124 |
| RansomLook — Dernière mise à jour | 15 jan. 2025 07:45 |

### Répartition par sévérité (emails)
- 🔴 CRITICAL : 1 compte
- 🟠 HIGH : 2 comptes  
- 🟡 MEDIUM : 2 comptes
- 🟢 LOW : 0 compte

---

## 🚨 Comptes compromis

### alice@mondomaine.fr — 🔴 CRITICAL

**Fuite dans 3 services :**

| Service | Date | Types de données | Sensible |
|---|---|---|---|
| ServiceXYZ | Mars 2024 | Email, Mot de passe | ⚠️ Credential détecté (masqué) |
| Adobe | Oct. 2013 | Email, Password hint | ⚠️ Hash détecté (masqué) |
| Dropbox | Jul. 2012 | Email | — |

**Actions recommandées :**
1. Forcer la réinitialisation du mot de passe
2. Activer le MFA sur ce compte
3. Révoquer toutes les sessions actives
4. Auditer les accès récents dans les logs

---

### bob@mondomaine.fr — ✅ Aucune fuite détectée

---

## ✅ Comptes sans anomalie détectée (82)
*(liste non affichée pour des raisons de confidentialité)*

---

## 🔒 Attestation d'intégrité
- Aucun mot de passe, hash ou credential n'a été stocké
- Le sanitizer a été appliqué sur toutes les données brutes (hors données RansomLook — publiques)
- Les données temporaires ont été purgées en mémoire après génération du rapport
- L'URL du portail .onion n'est pas incluse dans ce rapport
```

---

## 10. Sécurité & vie privée by design

### 10.1 Règles de code impératives

```python
# RÈGLE 1 : Aucun log de données sensibles
# ❌ Interdit
logger.debug(f"Password found: {password}")
logger.info(f"Hash: {hash_value}")

# ✅ Autorisé
logger.debug(f"Sensitive credential detected for {email} — masked")
logger.info(f"Finding processed: has_password={finding.has_password}")

# RÈGLE 2 : Purge mémoire après usage
import ctypes, gc

def purge_sensitive(data: str) -> None:
    """Écrase la chaîne en mémoire avant de la libérer."""
    if data:
        ctypes.memset(id(data), 0, len(data))
    del data
    gc.collect()

# RÈGLE 3 : Jamais de sérialisation de données brutes
# Le modèle Pydantic LeakFinding ne contient aucun champ sensible
# La sérialisation JSON ne peut donc pas les exposer
```

### 10.2 Secrets management

- Toutes les clés API sont dans `.env` (jamais commitées — `.gitignore` obligatoire).
- En production : utiliser **HashiCorp Vault** ou **AWS Secrets Manager**.
- Le pre-commit hook **detect-secrets** scanne chaque commit.

### 10.3 Politique de rétention

```
Données traitées en mémoire uniquement
        │
        ├── Données brutes API → Sanitizer → Purge immédiate
        │
        ├── Findings sanitisés → Aggregator → Rapport → Purge
        │
        └── Rapport final → Fichier (JSON/MD/PDF) → Seul artefact persisté
              └── Contient : emails compromis + noms de breaches + flags booléens
              └── Ne contient PAS : passwords, hashs, tokens, clés API
```

### 10.4 Sécurité réseau

- Toutes les requêtes HTTP externes via **HTTPS uniquement** (vérification SSL stricte).
- Support proxy SOCKS5/HTTP configurable (pour cloisonner les requêtes OSINT).
- Rate limiting respecté scrupuleusement pour chaque API externe.
- Timeout configuré sur toutes les requêtes (défaut : 30s).
- User-Agent identifiable et honnête (pas d'usurpation).
- **RansomLook** : communication uniquement en HTTP local (container-to-container ou localhost). L'API n'est **jamais** exposée sur une interface réseau publique (`127.0.0.1:8888` uniquement dans le `docker-compose.yml`).
- **Tor via RansomLook** : le trafic vers les sites .onion passe par le container Tor dédié — LeakMonitor lui-même ne fait aucune connexion Tor directe.

---

## 11. Structure du projet et README

### 11.1 Arborescence

```
leakmonitor/
├── README.md
├── pyproject.toml
├── Makefile
├── .env.example               # Template — JAMAIS de vraies clés ici
├── .gitignore                 # Inclut .env, reports/, *.log, *.session
├── docker-compose.yml         # LeakMonitor + RansomLook (app + redis + tor)
├── Dockerfile
│
├── leakmonitor/               # Package principal
│   ├── __init__.py
│   ├── main.py                # Point d'entrée CLI (Typer)
│   ├── config/
│   │   ├── settings.py        # Pydantic Settings
│   │   ├── sources.yaml       # Activation/désactivation de chaque source
│   │   └── group_names.yaml   # Mapping noms techniques → affichables (ransomware)
│   │
│   ├── core/
│   │   ├── orchestrator.py    # Chef d'orchestre des scans
│   │   ├── sanitizer.py       # Couche de nettoyage des données
│   │   ├── aggregator.py      # Déduplication et agrégation (email + ransom)
│   │   ├── ransom_tracker.py  # Orchestration RansomLook + alerte immédiate
│   │   └── scheduler.py       # APScheduler
│   │
│   ├── clients/               # Un fichier par source
│   │   ├── base.py            # Classe abstraite BaseLeakClient
│   │   ├── hibp.py
│   │   ├── leakcheck.py
│   │   ├── dehashed.py
│   │   ├── intelx.py
│   │   ├── github_monitor.py
│   │   ├── gitlab_monitor.py
│   │   ├── pastebin_monitor.py
│   │   ├── telegram_monitor.py
│   │   ├── urlscan.py
│   │   ├── otx.py
│   │   └── ransomlook.py      # Client HTTP → instance Docker RansomLook
│   │
│   ├── resolver/
│   │   └── email_resolver.py  # Découverte des emails du domaine
│   │
│   ├── models/
│   │   ├── finding.py         # LeakFinding, AggregatedReport
│   │   ├── ransom.py          # RansomFinding, RansomStats, RansomStatus
│   │   └── report.py          # FinalReport, ReportMetadata
│   │
│   ├── report/
│   │   ├── engine.py          # Générateur de rapports (gère section ransomware)
│   │   └── templates/
│   │       ├── report.md.j2
│   │       ├── report.html.j2
│   │       └── notification.txt.j2
│   │
│   └── notifications/
│       └── engine.py          # Inclut send_ransom_alert()
│
├── tests/
│   ├── conftest.py
│   ├── test_sanitizer.py
│   ├── test_aggregator.py
│   ├── test_ransom_tracker.py # Tests du module ransom
│   ├── test_clients/
│   │   ├── test_hibp.py
│   │   ├── test_ransomlook.py # Mocks de l'API RansomLook locale
│   │   └── ...
│   └── fixtures/
│       ├── mock_responses/    # Réponses API mockées pour les tests
│       └── ransomlook/
│           ├── victim_found.json    # Réponse simulée : domaine trouvé
│           └── victim_not_found.json # Réponse simulée : domaine absent
│
└── reports/                   # Répertoire de sortie (gitignored)
    └── .gitkeep
```

### 11.2 README.md (contenu complet)

```markdown
# LeakMonitor

Outil de détection de fuites de données ciblé sur un domaine.
Usage légal — surveillance défensive de votre propre domaine uniquement.

## Prérequis

- Python 3.12+
- uv (gestionnaire de paquets) : `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker + Docker Compose v2 (requis pour RansomLook)

## Installation

```bash
# Cloner le projet
git clone https://github.com/yourorg/leakmonitor.git
cd leakmonitor

# Installer les dépendances Python
uv sync

# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API (voir section "Configuration" ci-dessous)
# En particulier : TARGET_DOMAIN et RANSOMLOOK_SEARCH_TERMS
```

## Démarrage de RansomLook (requis)

RansomLook tourne dans Docker et doit être démarré avant LeakMonitor.

```bash
# Démarrer uniquement la stack RansomLook pour le premier peuplement
docker-compose up ransomlook-redis ransomlook-tor ransomlook-app -d

# Surveiller le premier cycle de scraping (10-30 minutes)
docker-compose logs -f ransomlook-app

# Vérifier que l'API est opérationnelle
curl http://localhost:8888/api/v1/stats

# Tester la recherche sur votre domaine
curl "http://localhost:8888/api/v1/victim?name=mondomaine.fr"
```

## Démarrage complet (LeakMonitor + RansomLook)

```bash
docker-compose up -d
```

## Utilisation (sans Docker)

```bash
# Vérifier que RansomLook est joignable
uv run python -m leakmonitor ransomlook --health

# Scan complet (toutes sources configurées)
uv run python -m leakmonitor scan

# Scan avec rapport HTML
uv run python -m leakmonitor scan --format html

# Scan uniquement RansomLook (rapide, vérification d'urgence)
uv run python -m leakmonitor ransomlook --check

# Scan d'un email spécifique
uv run python -m leakmonitor check --email alice@mondomaine.fr

# Activer le scheduler (tourne en arrière-plan)
uv run python -m leakmonitor schedule --start

# Vérifier l'état de toutes les sources
uv run python -m leakmonitor sources --status

# Lancer les tests
make test
```

## Rapport

Les rapports sont générés dans `./reports/` au format JSON + Markdown.
Aucune donnée sensible (mot de passe, hash, clé API, URL .onion) n'est
incluse dans les rapports.

## Avertissement légal

Cet outil est conçu exclusivement pour surveiller votre propre domaine.
L'utilisation sur des domaines ne vous appartenant pas peut constituer
une infraction au Code Pénal (Art. 323-1) et au RGPD.
```

---

## 12. Configuration des clés API et services

### 12.1 HaveIBeenPwned

```
URL : https://haveibeenpwned.com/API/Key
Procédure :
  1. Se rendre sur https://haveibeenpwned.com/API/Key
  2. Saisir une adresse email valide
  3. Choisir un abonnement (recommandé : abonnement mensuel ~3,50 USD)
  4. Payer via Stripe
  5. Recevoir la clé API par email
  6. Ajouter dans .env : HIBP_API_KEY=votre_clé_ici

Note : Pour le Domain Search (scan complet d'un domaine), l'abonnement
       annuel (~550 USD) est nécessaire. Sans lui, les emails doivent
       être vérifiés un par un (1500ms entre chaque requête).
```

### 12.2 GitHub Personal Access Token

```
URL : https://github.com/settings/tokens/new
Procédure :
  1. Connecté à GitHub → Settings → Developer settings → Personal access tokens
  2. "Generate new token (classic)"
  3. Scopes requis : public_repo (lecture seule sur repos publics)
  4. Durée : 90 jours ou "No expiration" (selon votre politique)
  5. Ajouter dans .env : GITHUB_TOKEN=ghp_votre_token_ici

Rate limit avec token : 5000 req/h (vs 60/h sans token)
```

### 12.3 GitLab Personal Access Token

```
URL : https://gitlab.com/-/user_settings/personal_access_tokens
Procédure :
  1. Connecté à GitLab → Preferences → Access Tokens
  2. Scopes requis : read_api
  3. Ajouter dans .env : GITLAB_TOKEN=glpat-votre_token_ici
```

### 12.4 LeakCheck.io

```
URL : https://leakcheck.io/api
Procédure :
  1. Créer un compte sur https://leakcheck.io
  2. Plans : Free (10 req/jour), Basic (~10 USD/mois), Pro (~50 USD/mois)
  3. Dashboard → API → Copy API Key
  4. Ajouter dans .env : LEAKCHECK_API_KEY=votre_clé_ici
```

### 12.5 Dehashed

```
URL : https://www.dehashed.com/register
Procédure :
  1. Créer un compte sur https://www.dehashed.com
  2. Plans : $5.49/mois (personal) à $179.99/mois (enterprise)
  3. Account → API Key
  4. Ajouter dans .env :
     DEHASHED_EMAIL=votre_email_dehashed@example.com
     DEHASHED_API_KEY=votre_clé_ici
  
  L'API Dehashed utilise Basic Auth (email:api_key en base64)
```

### 12.6 Intelligence X (IntelX)

```
URL : https://intelx.io/account?tab=developer
Procédure :
  1. Créer un compte sur https://intelx.io
  2. Plans : Free (très limité), Developer (~100 EUR/mois)
  3. Account → API → Create API Key
  4. Ajouter dans .env : INTELX_API_KEY=votre_clé_ici
  
  Endpoints utilisés :
  - POST https://2.intelx.io/intelligent/search
  - GET  https://2.intelx.io/intelligent/search/result?id={searchId}
```

### 12.7 Shodan

```
URL : https://account.shodan.io/
Procédure :
  1. Créer un compte sur https://shodan.io
  2. Plan gratuit disponible (très limité)
  3. Plan Member : ~65 USD (one-time)
  4. Account Overview → API Key (visible directement)
  5. Ajouter dans .env : SHODAN_API_KEY=votre_clé_ici
```

### 12.8 URLScan.io

```
URL : https://urlscan.io/user/signup
Procédure :
  1. Créer un compte gratuit sur https://urlscan.io
  2. API Keys → Create new API key
  3. Permissions : Search (lecture seule suffit)
  4. Ajouter dans .env : URLSCAN_API_KEY=votre_clé_ici
  
  Plan gratuit : 60 req/min, suffisant pour notre usage
```

### 12.9 AlienVault OTX

```
URL : https://otx.alienvault.com/accounts/register
Procédure :
  1. Créer un compte gratuit sur https://otx.alienvault.com
  2. Settings → API Integration → OTX Key
  3. Ajouter dans .env : OTX_API_KEY=votre_clé_ici
  
  Entièrement gratuit
```

### 12.10 Telegram API (pour monitoring canaux publics)

```
URL : https://my.telegram.org/apps
Procédure :
  1. Se connecter sur https://my.telegram.org avec votre numéro Telegram
  2. "API Development Tools"
  3. Créer une nouvelle application (nom : LeakMonitor, plateforme : Other)
  4. Récupérer api_id et api_hash
  5. Ajouter dans .env :
     TELEGRAM_API_ID=12345678
     TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
  
  Note : Usage réservé aux canaux PUBLICS uniquement.
         Telethon demandera une authentification par SMS au premier lancement.
         La session sera stockée chiffrée localement.
```

### 12.11 Pastebin Pro

```
URL : https://pastebin.com/pro
Procédure :
  1. Souscrire à un compte Pro (~5 USD/mois)
  2. Permet l'accès à l'API scraping : https://scrape.pastebin.com/api_scraping.php
  3. Votre IP doit être whitelistée : https://pastebin.com/doc_scraping_api
  4. Pas de clé API — l'accès est basé sur l'IP

  Alternative gratuite : utiliser Pwnbin (https://github.com/kahunalu/pwnbin)
  qui surveille plusieurs paste sites sans authentification.
```

### 12.12 RansomLook — Configuration Docker

```
Dépôt GitHub : https://github.com/RansomLook/RansomLook
Image Docker  : ghcr.io/ransomlook/ransomlook:latest
Pas de clé API nécessaire pour l'instance auto-hébergée.

Procédure de démarrage :

  1. S'assurer que Docker et Docker Compose v2 sont installés :
       docker --version       # >= 24.x
       docker compose version # >= 2.x

  2. Le fichier docker-compose.yml fourni avec LeakMonitor inclut
     déjà la configuration complète (app + redis + tor).
     Aucun fichier de configuration supplémentaire n'est nécessaire.

  3. Premier démarrage :
       docker-compose up ransomlook-redis ransomlook-tor ransomlook-app -d

  4. Attendre le premier cycle de scraping (10 à 30 minutes selon
     la disponibilité des sites .onion via Tor) :
       docker-compose logs -f ransomlook-app
     Attendre le message : "Scraping complete — X posts indexed"

  5. Vérifier l'API :
       curl http://localhost:8888/api/v1/stats
     Réponse attendue (exemple) :
       {"groups": 124, "posts": 16340, "last_update": "2025-01-15T..."}

  6. Ajouter dans .env :
       RANSOMLOOK_URL=http://localhost:8888
       RANSOMLOOK_SEARCH_TERMS=MonDomaine,Mon Domaine SA

       Note : Si vous utilisez docker-compose (LeakMonitor dans Docker),
       l'URL doit être :
       RANSOMLOOK_URL=http://ransomlook-app:8888
       (communication inter-container, pas localhost)

  7. Commandes de maintenance :
       # Forcer un refresh immédiat des données
       docker-compose exec ransomlook-app python update.py

       # Vérifier le nombre de groupes suivis
       curl http://localhost:8888/api/v1/groups | python3 -c \
         "import sys, json; g=json.load(sys.stdin); print(f'{len(g)} groupes')"

       # Sauvegarder les données Redis
       docker-compose exec ransomlook-redis redis-cli BGSAVE

       # Mettre à jour l'image vers la dernière version
       docker-compose pull ransomlook-app
       docker-compose up -d ransomlook-app

  8. (Optionnel) Instance publique ransomlook.io :
     Si vous préférez utiliser l'instance publique plutôt que l'auto-hébergement :
       RANSOMLOOK_URL=https://www.ransomlook.io
     Avantages : pas de maintenance Docker, données toujours fraîches
     Inconvénients : dépendance externe, pas de contrôle sur la disponibilité,
                     vos termes de recherche transitent par un tiers
```

---

## 13. Plan de tests

### 13.1 Tests unitaires

```
tests/
├── test_sanitizer.py          # Vérifier que les données sensibles sont bien masquées
│   ├── test_password_masked
│   ├── test_hash_masked (MD5, SHA-1, SHA-256, bcrypt)
│   ├── test_api_key_masked
│   └── test_base64_masked
│
├── test_aggregator.py         # Déduplication et calcul de sévérité
│   ├── test_dedup_same_breach_multiple_sources
│   ├── test_severity_calculation
│   ├── test_ransom_finding_elevates_global_severity
│   └── test_empty_findings
│
├── test_ransom_tracker.py     # Module RansomLook
│   ├── test_domain_found_triggers_critical
│   ├── test_domain_not_found_returns_empty
│   ├── test_multi_term_search_deduplicates
│   ├── test_unhealthy_instance_handled_gracefully
│   └── test_immediate_alert_on_finding
│
└── test_clients/
    ├── test_hibp.py           # Mock des réponses HTTP avec respx
    ├── test_ransomlook.py     # Mock de l'API RansomLook locale
    │   ├── test_victim_search_found        # Fixture: victim_found.json
    │   ├── test_victim_search_not_found    # Fixture: victim_not_found.json
    │   ├── test_health_check_ok
    │   ├── test_health_check_instance_down
    │   └── test_retry_on_connection_error
    ├── test_leakcheck.py
    └── test_github.py
```

**Fixture `tests/fixtures/ransomlook/victim_found.json` :**
```json
[
  {
    "post_title": "MonDomaine SA",
    "group_name": "lockbit3",
    "discovered": "2025-01-14T14:32:00Z",
    "published": "2025-01-14T14:32:00Z",
    "post_url": "http://lockbit3abc.onion/post/abc123",
    "description": "500GB of internal data.",
    "website": "mondomaine.fr",
    "country": "France",
    "activity": "Technology",
    "claim_size": "500GB",
    "added": "2025-01-14T15:00:00Z"
  }
]
```

**Fixture `tests/fixtures/ransomlook/victim_not_found.json` :**
```json
[]
```

### 13.2 Tests d'intégration

```bash
# Tester avec de vraies clés API sur une adresse de test connue
# HIBP propose l'adresse "test@example.com" pour les tests
uv run pytest tests/integration/ --api-keys-required -v

# Tester RansomLook en intégration (nécessite l'instance Docker active)
uv run pytest tests/integration/test_ransomlook_live.py --ransomlook-required -v
```

### 13.3 Tests de non-régression sécurité

```python
# tests/test_security.py

def test_no_sensitive_data_in_report():
    """Le rapport final ne doit contenir aucune donnée sensible."""
    report_json = generate_report(mock_findings_with_passwords)
    for pattern in SENSITIVE_PATTERNS:
        assert not re.search(pattern, json.dumps(report_json)), \
            f"Sensitive data leaked in report via pattern: {pattern}"

def test_ransomlook_onion_url_not_in_report():
    """L'URL .onion du portail ransomware ne doit pas apparaître dans le rapport."""
    report_json = generate_report_with_ransom_finding(mock_ransom_finding)
    assert ".onion" not in json.dumps(report_json), \
        "URL .onion présente dans le rapport — doit être masquée"

def test_sanitizer_complete_coverage():
    """Le sanitizer doit couvrir tous les formats connus."""
    # 20+ cas de test couvrant tous les formats de hash courants
```

### 13.4 Commandes Make

```makefile
.PHONY: install test lint type-check scan report clean ransomlook-up ransomlook-down ransomlook-check ransomlook-update

install:
	uv sync

test:
	uv run pytest tests/unit/ -v --cov=leakmonitor --cov-report=html

test-ransomlook:
	uv run pytest tests/test_clients/test_ransomlook.py tests/test_ransom_tracker.py -v

test-integration:
	uv run pytest tests/integration/ --api-keys-required -v

lint:
	uv run ruff check leakmonitor/ tests/
	uv run ruff format --check leakmonitor/ tests/

type-check:
	uv run mypy leakmonitor/

scan:
	uv run python -m leakmonitor scan

scan-ransom:
	uv run python -m leakmonitor ransomlook --check

report:
	uv run python -m leakmonitor scan --format markdown,json,html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf reports/*.json reports/*.md reports/*.html reports/*.pdf

sources-status:
	uv run python -m leakmonitor sources --status

# ─── Commandes RansomLook ──────────────────────────────────────
ransomlook-up:
	docker-compose up ransomlook-redis ransomlook-tor ransomlook-app -d
	@echo "En attente du premier cycle de scraping..."
	@sleep 5
	@docker-compose logs --tail=20 ransomlook-app

ransomlook-down:
	docker-compose stop ransomlook-redis ransomlook-tor ransomlook-app

ransomlook-check:
	curl -s http://localhost:8888/api/v1/stats | python3 -m json.tool
	@echo ""
	@echo "Recherche du domaine cible :"
	curl -s "http://localhost:8888/api/v1/victim?name=$(TARGET_DOMAIN)" | python3 -m json.tool

ransomlook-update:
	docker-compose pull ransomlook-app
	docker-compose up -d ransomlook-app

ransomlook-logs:
	docker-compose logs -f ransomlook-app

# ──────────────────────────────────────────────────────────────
docker-build:
	docker build -t leakmonitor:latest .

docker-run:
	docker-compose up --build
```

---

## 14. Roadmap et évolutions

### Phase 1 — MVP (4-6 semaines)
- [ ] Infrastructure de base (config, sanitizer, models)
- [ ] **Déploiement Docker RansomLook** (stack complète : app + redis + tor)
- [ ] **Client RansomLookClient + RansomwareTracker** (recherche multi-termes, alerte immédiate)
- [ ] **Modèle RansomFinding** + intégration dans l'Aggregator
- [ ] Intégration HIBP (email par email)
- [ ] Intégration GitHub monitoring
- [ ] Rapport Markdown + JSON (avec section ransomware en tête)
- [ ] Tests unitaires >80% coverage (incluant test_ransomlook.py)

> **Pourquoi RansomLook dès la Phase 1 ?** C'est la seule source entièrement gratuite qui couvre le scénario de risque le plus élevé (compromission massive en cours). Elle ne nécessite pas de clé API et son déploiement Docker est simple et documenté. Le rapport sans cette dimension est incomplet.

### Phase 2 — Enrichissement sources (4-6 semaines)
- [ ] Intégration LeakCheck + Dehashed
- [ ] Monitoring Pastebin via Pwnbin
- [ ] Domain Email Resolver (Hunter.io + theHarvester)
- [ ] Rapport HTML avec dashboard visuel (section ransomware mise en évidence)
- [ ] Scheduler + notifications email (alerte ransomware immédiate configurée)

### Phase 3 — Monitoring continu (4-6 semaines)
- [ ] Feed Monitor Telegram (canaux publics)
- [ ] Monitoring GitHub en temps réel (webhooks ou polling)
- [ ] Intégration IntelX (si budget)
- [ ] Conteneurisation Docker complète (LeakMonitor + RansomLook en un seul `docker-compose up`)
- [ ] Export PDF

### Phase 4 — Hardening (2-4 semaines)
- [ ] Audit sécurité du code (bandit, semgrep)
- [ ] Rotation automatique des clés API expirées
- [ ] Chiffrement des rapports au repos (Fernet)
- [ ] Dashboard web minimaliste (FastAPI + HTMX)
- [ ] Documentation complète (mkdocs)
- [ ] Alertes RansomLook via PagerDuty / OpsGenie (intégration webhook)

---

## Annexe A — Comparatif des sources par rapport coût/efficacité

| Source | Coût mensuel | Couverture | Fraîcheur | Recommandation |
|---|---|---|---|---|
| HIBP (email) | ~3,50 USD | ★★★★★ | Bonne | **Indispensable** |
| HIBP Domain Search | ~45 USD | ★★★★★ | Bonne | Recommandé si budget |
| GitHub | Gratuit | ★★★☆☆ | Temps réel | **Indispensable** |
| URLScan | Gratuit | ★★★☆☆ | Bonne | **Indispensable** |
| OTX AlienVault | Gratuit | ★★★☆☆ | Bonne | **Indispensable** |
| **RansomLook** | **Gratuit** (Docker) | **★★★★★** | **Quasi temps réel** | **Indispensable** |
| LeakCheck | ~10 USD | ★★★★☆ | Bonne | Très recommandé |
| Dehashed | ~5 USD | ★★★★☆ | Moyenne | Très recommandé |
| IntelX | ~100 EUR | ★★★★★ | Excellente | Si budget avancé |
| Telegram monitoring | Gratuit | ★★☆☆☆ | Temps réel | Optionnel |

> **Note RansomLook** : La couverture ★★★★★ s'applique au scénario ransomware spécifiquement. Pour les fuites de credentials "classiques", RansomLook n'apporte rien — c'est HIBP et les autres qui prennent le relais. Les deux dimensions sont complémentaires et non substituables.

## Annexe B — Ressources et références

- Troy Hunt — Blog HIBP : https://www.troyhunt.com
- NIST SP 800-63B (gestion des identifiants) : https://pages.nist.gov/800-63-3/
- ANSSI — Guide de la sécurité des mots de passe : https://www.ssi.gouv.fr
- CNIL — Violations de données : https://www.cnil.fr/fr/les-violations-de-donnees
- RFC 8959 (k-anonymity pour les mots de passe) : https://www.rfc-editor.org/rfc/rfc8959
- theHarvester (OSINT email discovery) : https://github.com/laramies/theHarvester
- Pwnbin (paste sites monitor) : https://github.com/kahunalu/pwnbin
- **RansomLook (dépôt GitHub)** : https://github.com/RansomLook/RansomLook
- **RansomLook (instance publique)** : https://www.ransomlook.io
- ANSSI — Attaques par rançongiciel : https://www.ssi.gouv.fr/guide/attaques-par-ransomware-tous-concernes/
- CISA Known Ransomware Groups : https://www.cisa.gov/stopransomware

---

*Ce document constitue la spécification technique complète du projet LeakMonitor.  
Toute implémentation doit respecter le cadre légal décrit en Section 2.  
Pour toute question, se référer à la politique RGPD de votre organisation.*
