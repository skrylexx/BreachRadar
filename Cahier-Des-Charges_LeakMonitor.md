# Cahier des Charges Technique — LeakMonitor
## Système de détection de fuites de données ciblé sur un domaine

---

> **Version** : 1.0  
> **Statut** : Draft  
> **Cadre** : Usage légal — surveillance de son propre domaine (OSINT défensif)

---

## Table des matières

1. [Contexte et état de l'art](#1-contexte-et-état-de-lart)
2. [Cadre légal](#2-cadre-légal)
3. [Périmètre du projet](#3-périmètre-du-projet)
4. [Architecture générale](#4-architecture-générale)
5. [Stack technique](#5-stack-technique)
6. [Sources de données](#6-sources-de-données)
7. [Modules fonctionnels](#7-modules-fonctionnels)
8. [Modèle de rapport](#8-modèle-de-rapport)
9. [Sécurité & vie privée by design](#9-sécurité--vie-privée-by-design)
10. [Structure du projet et README](#10-structure-du-projet-et-readme)
11. [Configuration des clés API](#11-configuration-des-clés-api)
12. [Plan de tests](#12-plan-de-tests)
13. [Roadmap et évolutions](#13-roadmap-et-évolutions)

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
Ajouter une dimension **Early Warning System** à l'aide de RansomLook :
- Nouvel indicateur de compromission (IoC) : Le nom de l'organisation ou le nom de domaine sur un site de "Name & Shame" de groupe de ransomware.
- On ne cherche plus seulement si user@domain.fr est dans une base, mais si domain.fr est listé comme victime d'un groupe (LockBit, BlackCat, etc.) avant même que les données ne soient téléchargeables.

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
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        LeakMonitor                                                  │
│                                                                                     │
│  ┌───────────────┐     ┌──────────────┐     ┌──────────────────┐                    │
│  │  Scheduler    │───▶│ Orchestrator │───▶ │  Report Engine   │                    │
│  │  (APScheduler │     │ (Async Core) │     │  (Jinja2 + JSON) │                    │
│  │   / Cron)     │     │              │     │                  │                    │
│  └───────────────┘     └──────┬───────┘     └──────────────────┘                    │
│                               │                                                     │
│              ┌────────────────┼──────────────|──────────────────────┐               │
│              ▼                ▼              ▼                      ▼               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐       │
│  │  API Clients │  │ Feed Monitor │  │ Local HIBP   │  | Local RansomLook   |       │
│  │              │  │              │  │ Dataset      │  | Ransomware Tracker |       │
│  │ - HIBP API   │  │ - Pastebin   │  │ (Optional)   │  | (Recommanded)      |       │
│  │ - IntelX     │  │ - GH/GL      │  │              │  |                    |       │
│  │ - LeakCheck  │  │ - Telegram   │  └──────────────┘  └────────────────────┘       │
│  │ - Dehashed   │  │              │                                                 │
│  └──────────────┘  └──────────────┘                                                 │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────┐                       │
│  │              Anonymizer / Sanitizer Layer                │                       │
│  │  (Masquage des mots de passe, hashs, clés API, tokens)   │                       │
│  └──────────────────────────────────────────────────────────┘                       │
│                                                                                     │
│  ┌──────────────┐                                                                   │
│  │  No-Storage  │  Aucune donnée personnelle persistée                              │
│  │  Policy      │  (traitement en mémoire uniquement)                               │
│  └──────────────┘                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Flux de données

```
1. Scheduler déclenche une analyse (manuelle ou planifiée)
2. L'Orchestrator charge la config (domaine cible, sources activées, clés API)
3. Chaque module source est appelé en parallèle (asyncio)
4. Les résultats bruts transitent par le Sanitizer (masquage immédiat)
5. L'Orchestrator déduplique et agrège les findings
6. Le Report Engine génère le rapport final (JSON + Markdown/HTML)
7. Les données brutes sont purgées de la mémoire
8. (Optionnel) Notification par email/webhook
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

#### 6.1.9 RansomLook (gratuit si hébergé)
- **URL** : `https://www.ransomlook.io/doc/` #URL de la documentation API, à déployer en interne
- **Auth** : Clé API (gratuit illimité)

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

## 7. Modules fonctionnels

### 7.1 Configuration Manager

```
config/
├── settings.py          # Pydantic Settings — lecture .env + validation
├── sources.yaml         # Activation/désactivation de chaque source
└── templates/
    └── report.html.j2   # Template Jinja2 du rapport
```

**Fichier `.env` :**
```dotenv
# Domaine cible (IMMUABLE dans ce projet)
TARGET_DOMAIN=mondomaine.fr

# Clés API (voir Section 11 pour obtenir chacune)
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

### 7.2 Domain Email Resolver

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

### 7.3 API Clients (un par source)

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

### 7.4 Sanitizer Layer

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

### 7.5 Deduplicator & Aggregator

```python
class ResultAggregator:
    """
    - Déduplique les findings identiques provenant de sources multiples
    - Agrège par email, par breach, par type de données
    - Calcule un score de sévérité global par email

    !! ATTENTION
    Si le domaine apparaît sur RansomLook, la sévérité doit être CRITICAL, et une alerte immédiate doit être envoyée car cela signifie qu'une exfiltration massive de données est en cours ou terminée.
    """
    
    def aggregate(self, findings: list[LeakFinding]) -> AggregatedReport: ...
```

**Calcul de sévérité :**

| Condition | Niveau |
|---|---|
| Fuite ancienne (> 3 ans), pas de credentials | LOW |
| Email + données PII uniquement | MEDIUM |
| Email + hash de mot de passe présent | HIGH |
| Email + mot de passe en clair ou clé API | CRITICAL |
| Fuite récente (< 6 mois) + tout type | +1 niveau |

### 7.6 Feed Monitor (surveillance continue)

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

### 7.7 Scheduler

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

### 7.8 Notification Engine (optionnel)

```python
class NotificationEngine:
    async def send_email(self, report: FinalReport, recipient: str): ...
    async def send_webhook(self, report: FinalReport, webhook_url: str): ...
    async def send_slack(self, report: FinalReport, channel: str): ...
```

**Note** : Les notifications ne contiennent que le résumé (nombre de comptes compromis, sévérité max) — jamais de données sensibles.

### 7.9 RansomwareTracker (si RansomLook déployé)

```python
class RansomwareTracker(BaseLeakClient):
    name: "RansomLook"
    
    async def check_domain(self, domain: str) -> list[LeakFinding]:
        """
        Requête RansomLook pour voir si le domaine apparaît 
        sur un blog de ransomware.
        """
        # Si trouvé, génère un Finding de sévérité CRITICAL
        # même si aucun email individuel n'est encore leaké.
```

---

## 8. Modèle de rapport

### 8.1 Structure JSON (format brut)

```json
{
  "report_metadata": {
    "generated_at": "2025-01-15T08:00:00Z",
    "target_domain": "mondomaine.fr",
    "sources_queried": ["hibp", "leakcheck", "github", "dehashed"],
    "sources_errors": [],
    "scan_duration_seconds": 42.3,
    "total_emails_checked": 87,
    "total_findings": 12
  },
  "summary": {
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
    "data_purged_after_report": true
  }
}
```

### 8.2 Rapport Markdown (format humain)

```markdown
# 🔍 Rapport LeakMonitor — mondomaine.fr
**Généré le** : 15 janvier 2025 à 08:00  
**Sources consultées** : HIBP, LeakCheck, GitHub, Dehashed  
**Durée d'analyse** : 42 secondes

---

## 📊 Résumé

| Indicateur | Valeur |
|---|---|
| Emails analysés | 87 |
| **Emails compromis** | **5** |
| Sévérité maximale | 🔴 CRITICAL |
| Fuite la plus récente | 15 mars 2024 |
| Sources en erreur | Aucune |

### Répartition par sévérité
- 🔴 CRITICAL : 1 compte
- 🟠 HIGH : 2 comptes  
- 🟡 MEDIUM : 2 comptes
- 🟢 LOW : 0 compte

---

## 💀 Alertes Ransomware (via RansomLook)

Statut : **DOMAINE DÉTECTÉ**
Groupe : *LockBit 3.0*

Date de publication : 2026-04-20
Description : "500GB of internal data, including SQL databases and employee emails."

Note : Les données n'ont pas encore été publiées (période de négociation). Risque de fuite massive imminent.

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
- Le sanitizer a été appliqué sur toutes les données brutes
- Les données temporaires ont été purgées en mémoire après génération du rapport
```

---

## 9. Sécurité & vie privée by design

### 9.1 Règles de code impératives

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

### 9.2 Secrets management

- Toutes les clés API sont dans `.env` (jamais commitées — `.gitignore` obligatoire).
- En production : utiliser **HashiCorp Vault** ou **AWS Secrets Manager**.
- Le pre-commit hook **detect-secrets** scanne chaque commit.

### 9.3 Politique de rétention

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

### 9.4 Sécurité réseau

- Toutes les requêtes HTTP via **HTTPS uniquement** (vérification SSL stricte).
- Support proxy SOCKS5/HTTP configurable (pour cloisonner les requêtes OSINT).
- Rate limiting respecté scrupuleusement pour chaque API.
- Timeout configuré sur toutes les requêtes (défaut : 30s).
- User-Agent identifiable et honnête (pas d'usurpation).

---

## 10. Structure du projet et README

### 10.1 Arborescence

```
leakmonitor/
├── README.md
├── pyproject.toml
├── Makefile
├── .env.example               # Template — JAMAIS de vraies clés ici
├── .gitignore                 # Inclut .env, reports/, *.log
├── docker-compose.yml
├── Dockerfile
│
├── leakmonitor/               # Package principal
│   ├── __init__.py
│   ├── main.py                # Point d'entrée CLI (Typer)
│   ├── config/
│   │   ├── settings.py        # Pydantic Settings
│   │   └── sources.yaml       # Configuration des sources
│   │
│   ├── core/
│   │   ├── orchestrator.py    # Chef d'orchestre des scans
│   │   ├── sanitizer.py       # Couche de nettoyage des données
│   │   ├── aggregator.py      # Déduplication et agrégation
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
│   │   └── otx.py
│   │
│   ├── resolver/
│   │   └── email_resolver.py  # Découverte des emails du domaine
│   │
│   ├── models/
│   │   ├── finding.py         # LeakFinding, AggregatedReport
│   │   └── report.py          # FinalReport, ReportMetadata
│   │
│   ├── report/
│   │   ├── engine.py          # Générateur de rapports
│   │   └── templates/
│   │       ├── report.md.j2
│   │       ├── report.html.j2
│   │       └── notification.txt.j2
│   │
│   └── notifications/
│       └── engine.py
│
├── tests/
│   ├── conftest.py
│   ├── test_sanitizer.py
│   ├── test_aggregator.py
│   ├── test_clients/
│   │   ├── test_hibp.py       # Avec mocks HTTP
│   │   └── ...
│   └── fixtures/
│       └── mock_responses/    # Réponses API mockées pour les tests
│
└── reports/                   # Répertoire de sortie (gitignored)
    └── .gitkeep
```

### 10.2 README.md (contenu complet)

```markdown
# LeakMonitor

Outil de détection de fuites de données ciblé sur un domaine.
Usage légal — surveillance défensive de votre propre domaine uniquement.

## Prérequis

- Python 3.12+
- uv (gestionnaire de paquets) : `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker (optionnel, pour exécution conteneurisée)

## Installation

```bash
# Cloner le projet
git clone https://github.com/yourorg/leakmonitor.git
cd leakmonitor

# Installer les dépendances avec uv
uv sync

# Copier et configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API (voir section "Configuration des clés API" ci-dessous)
```

## Configuration des clés API

Voir Section 11 de ce cahier des charges pour les instructions détaillées.

## Utilisation

```bash
# Scan complet (toutes sources configurées)
uv run python -m leakmonitor scan

# Scan avec rapport HTML
uv run python -m leakmonitor scan --format html

# Scan d'un email spécifique
uv run python -m leakmonitor check --email alice@mondomaine.fr

# Activer le scheduler (tourne en arrière-plan)
uv run python -m leakmonitor schedule --start

# Vérifier l'état des sources configurées
uv run python -m leakmonitor sources --status

# Lancer les tests
make test
```

## Via Docker

```bash
docker-compose up leakmonitor
```

## Rapport

Les rapports sont générés dans `./reports/` au format JSON + Markdown.
Aucune donnée sensible (mot de passe, hash, clé API) n'est incluse dans les rapports.

## Avertissement légal

Cet outil est conçu exclusivement pour surveiller votre propre domaine.
L'utilisation sur des domaines ne vous appartenant pas peut constituer
une infraction au Code Pénal (Art. 323-1) et au RGPD.
```

---

## 11. Configuration des clés API

### 11.1 HaveIBeenPwned

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

### 11.2 GitHub Personal Access Token

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

### 11.3 GitLab Personal Access Token

```
URL : https://gitlab.com/-/user_settings/personal_access_tokens
Procédure :
  1. Connecté à GitLab → Preferences → Access Tokens
  2. Scopes requis : read_api
  3. Ajouter dans .env : GITLAB_TOKEN=glpat-votre_token_ici
```

### 11.4 LeakCheck.io

```
URL : https://leakcheck.io/api
Procédure :
  1. Créer un compte sur https://leakcheck.io
  2. Plans : Free (10 req/jour), Basic (~10 USD/mois), Pro (~50 USD/mois)
  3. Dashboard → API → Copy API Key
  4. Ajouter dans .env : LEAKCHECK_API_KEY=votre_clé_ici
```

### 11.5 Dehashed

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

### 11.6 Intelligence X (IntelX)

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

### 11.7 Shodan

```
URL : https://account.shodan.io/
Procédure :
  1. Créer un compte sur https://shodan.io
  2. Plan gratuit disponible (très limité)
  3. Plan Member : ~65 USD (one-time)
  4. Account Overview → API Key (visible directement)
  5. Ajouter dans .env : SHODAN_API_KEY=votre_clé_ici
```

### 11.8 URLScan.io

```
URL : https://urlscan.io/user/signup
Procédure :
  1. Créer un compte gratuit sur https://urlscan.io
  2. API Keys → Create new API key
  3. Permissions : Search (lecture seule suffit)
  4. Ajouter dans .env : URLSCAN_API_KEY=votre_clé_ici
  
  Plan gratuit : 60 req/min, suffisant pour notre usage
```

### 11.9 AlienVault OTX

```
URL : https://otx.alienvault.com/accounts/register
Procédure :
  1. Créer un compte gratuit sur https://otx.alienvault.com
  2. Settings → API Integration → OTX Key
  3. Ajouter dans .env : OTX_API_KEY=votre_clé_ici
  
  Entièrement gratuit
```

### 11.10 Telegram API (pour monitoring canaux publics)

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

### 11.11 Pastebin Pro

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

---

## 12. Plan de tests

### 12.1 Tests unitaires

```
tests/
├── test_sanitizer.py         # Vérifier que les données sensibles sont bien masquées
│   ├── test_password_masked
│   ├── test_hash_masked (MD5, SHA-1, SHA-256, bcrypt)
│   ├── test_api_key_masked
│   └── test_base64_masked
│
├── test_aggregator.py        # Déduplication et calcul de sévérité
│   ├── test_dedup_same_breach_multiple_sources
│   ├── test_severity_calculation
│   └── test_empty_findings
│
└── test_clients/
    ├── test_hibp.py          # Mock des réponses HTTP avec respx
    ├── test_leakcheck.py
    └── test_github.py
```

### 12.2 Tests d'intégration

```bash
# Tester avec de vraies clés API sur une adresse de test connue
# HIBP propose l'adresse "test@example.com" pour les tests
uv run pytest tests/integration/ --api-keys-required -v
```

### 12.3 Tests de non-régression sécurité

```python
# tests/test_security.py

def test_no_sensitive_data_in_report():
    """Le rapport final ne doit contenir aucune donnée sensible."""
    # Injecter un finding avec des données sensibles
    # Vérifier que le rapport JSON ne contient aucun des patterns sensibles
    report_json = generate_report(mock_findings_with_passwords)
    
    for pattern in SENSITIVE_PATTERNS:
        assert not re.search(pattern, json.dumps(report_json)), \
            f"Sensitive data leaked in report via pattern: {pattern}"

def test_sanitizer_complete_coverage():
    """Le sanitizer doit couvrir tous les formats connus."""
    # 20+ cas de test couvrant tous les formats de hash courants
```

### 12.4 Commandes Make

```makefile
.PHONY: install test lint type-check scan report clean

install:
	uv sync

test:
	uv run pytest tests/unit/ -v --cov=leakmonitor --cov-report=html

lint:
	uv run ruff check leakmonitor/ tests/
	uv run ruff format --check leakmonitor/ tests/

type-check:
	uv run mypy leakmonitor/

scan:
	uv run python -m leakmonitor scan

report:
	uv run python -m leakmonitor scan --format markdown,json,html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	rm -rf reports/*.json reports/*.md reports/*.html reports/*.pdf

sources-status:
	uv run python -m leakmonitor sources --status

docker-build:
	docker build -t leakmonitor:latest .

docker-run:
	docker-compose up --build leakmonitor
```

---

## 13. Roadmap et évolutions

### Phase 1 — MVP (4-6 semaines)
- [ ] Infrastructure de base (config, sanitizer, models)
- [ ] Intégration HIBP (email par email)
- [ ] Intégration GitHub monitoring
- [ ] Rapport Markdown + JSON
- [ ] Tests unitaires >80% coverage

### Phase 2 — Enrichissement sources (4-6 semaines)
- [ ] Intégration LeakCheck + Dehashed
- [ ] Monitoring Pastebin via Pwnbin
- [ ] Domain Email Resolver (Hunter.io + theHarvester)
- [ ] Rapport HTML avec dashboard visuel
- [ ] Scheduler + notifications email

### Phase 3 — Monitoring continu (4-6 semaines)
- [ ] Feed Monitor Telegram (canaux publics)
- [ ] Monitoring GitHub en temps réel (webhooks ou polling)
- [ ] Intégration IntelX (si budget)
- [ ] Conteneurisation Docker complète
- [ ] Export PDF

### Phase 4 — Hardening (2-4 semaines)
- [ ] Audit sécurité du code (bandit, semgrep)
- [ ] Rotation automatique des clés API expirées
- [ ] Chiffrement des rapports au repos (Fernet)
- [ ] Dashboard web minimaliste (FastAPI + HTMX)
- [ ] Documentation complète (mkdocs)

---

## Annexe A — Comparatif des sources par rapport coût/efficacité

| Source | Coût mensuel | Couverture | Fraîcheur | Recommandation |
|---|---|---|---|---|
| HIBP (email) | ~3,50 USD | ★★★★★ | Bonne | **Indispensable** |
| HIBP Domain Search | ~45 USD | ★★★★★ | Bonne | Recommandé si budget |
| GitHub | Gratuit | ★★★☆☆ | Temps réel | **Indispensable** |
| URLScan | Gratuit | ★★★☆☆ | Bonne | **Indispensable** |
| OTX AlienVault | Gratuit | ★★★☆☆ | Bonne | **Indispensable** |
| LeakCheck | ~10 USD | ★★★★☆ | Bonne | Très recommandé |
| Dehashed | ~5 USD | ★★★★☆ | Moyenne | Très recommandé |
| IntelX | ~100 EUR | ★★★★★ | Excellente | Si budget avancé |
| Telegram monitoring | Gratuit | ★★☆☆☆ | Temps réel | Optionnel |
| RansomLook | Gratuit | ★★★★★ | Temps réel | Très recommandé |

## Annexe B — Ressources et références

- Troy Hunt — Blog HIBP : https://www.troyhunt.com
- NIST SP 800-63B (gestion des identifiants) : https://pages.nist.gov/800-63-3/
- ANSSI — Guide de la sécurité des mots de passe : https://www.ssi.gouv.fr
- CNIL — Violations de données : https://www.cnil.fr/fr/les-violations-de-donnees
- RFC 8959 (k-anonymity pour les mots de passe) : https://www.rfc-editor.org/rfc/rfc8959
- theHarvester (OSINT email discovery) : https://github.com/laramies/theHarvester
- Pwnbin (paste sites monitor) : https://github.com/kahunalu/pwnbin
- RansomLook (visuel sur ransomware) : https://www.ransomlook.io/

---

*Ce document constitue la spécification technique complète du projet LeakMonitor.  
Toute implémentation doit respecter le cadre légal décrit en Section 2.  
Pour toute question, se référer à la politique RGPD de votre organisation.*
