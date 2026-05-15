# TODO — Développement Frontend BreachRadar

> Branche de travail : `feat/frontend-pages`
> Référence : `Cahier-Des-Charges_BreachRadar.md`
> Stack : Next.js 15 (App Router) · TypeScript · Tailwind CSS · Shadcn/UI

---

## État actuel des pages

| Route | Fichier | État |
|---|---|---|
| `/` (dashboard) | `(dashboard)/page.tsx` | ✅ Partiel (mock data) |
| `/login` | `(auth)/login/page.tsx` | ✅ Présent |
| `/scans` | `(dashboard)/scans/page.tsx` | ✅ Présent |
| `/tools/hibp` | `(dashboard)/tools/hibp/page.tsx` | ✅ Présent |
| `/tools/github` | `(dashboard)/tools/github/page.tsx` | ✅ Présent |
| `/tools/ransomlook` | `(dashboard)/tools/ransomlook/page.tsx` | ✅ Présent |
| `/tools/leakcheck` | `(dashboard)/tools/leakcheck/page.tsx` | ✅ Présent |
| `/tools/urlscan` | `(dashboard)/tools/urlscan/page.tsx` | ✅ Présent |
| `/reports` | `(dashboard)/reports/page.tsx` | ✅ Présent |
| `/alerts/ransomware` | `(dashboard)/alerts/ransomware/page.tsx` | ✅ Présent |
| `/alerts/cve` | `(dashboard)/alerts/cve/page.tsx` | ✅ Présent |
| `/admin/users` | `(dashboard)/admin/users/page.tsx` | ✅ Présent |
| `/admin/api-keys` | `(dashboard)/admin/api-keys/page.tsx` | ✅ Présent |
| `/admin/smtp` | `(dashboard)/admin/smtp/page.tsx` | ✅ Présent |
| `/admin/scheduling` | `(dashboard)/admin/scheduling/page.tsx` | ✅ Présent |
| `/admin/audit` | `(dashboard)/admin/audit/page.tsx` | ✅ Présent |
| `/admin/settings` | `(dashboard)/admin/settings/page.tsx` | ✅ Présent |
| `/changelog` | `(dashboard)/changelog/page.tsx` | ✅ Présent |
| `/profile` | `(dashboard)/profile/page.tsx` | ✅ Présent |

---

## PHASE 0 — Fondations & Infrastructure UI

> Prérequis à toutes les pages. À faire en premier.

- [x] **0.1 — Design system tokens**
  - Vérifier / compléter `globals.css` : variables CSS pour les couleurs de sévérité (`--color-critical`, `--color-high`, `--color-medium`, `--color-low`)
  - Palette dark-first conforme au CDC : fond `#09090b`, surfaces `#18181b`, accent `#38bdf8`
  - Police `Inter` (UI) + `JetBrains Mono` (données techniques) via `next/font`

- [x] **0.2 — Composants Shadcn/UI manquants**
  - Installer : `badge`, `table`, `tabs`, `select`, `dialog`, `toast`, `skeleton`, `tooltip`, `switch`, `form`, `input`, `label`, `separator`, `dropdown-menu`, `alert`, `progress`
  - Vérifier que `button`, `card` sont déjà présents

- [x] **0.3 — Composants partagés custom**
  - `<SeverityBadge level="CRITICAL|HIGH|MEDIUM|LOW" />` — badge coloré réutilisable
  - `<StatusDot status="ok|warning|error" />` — indicateur de statut source
  - `<PageHeader title props breadcrumb />` — en-tête de page standard
  - `<EmptyState icon message action />` — état vide standard
  - `<DataTable columns data pagination />` — tableau paginé réutilisable (wrapper Tanstack Table ou Shadcn)
  - `<RadarSpinner />` — spinner animé type radar (SVG, utilisé pendant les scans)
  - `<TimeFilter value onChange />` — sélecteur 7j / 1 mois / 6 mois / 12 mois / Tout

- [x] **0.4 — i18n setup**
  - Installer et configurer `next-intl` (ou `next-i18next`)
  - Créer `messages/en.json` et `messages/fr.json` avec les clés de base
  - Ajouter le sélecteur langue dans le Header (icône globe + EN/FR)
  - Stocker la préférence en `localStorage` / cookie

- [x] **0.5 — Couche API client**
  - Créer `frontend/src/lib/api.ts` : client HTTP centralisé (fetch avec `NEXT_PUBLIC_API_URL`)
  - Fonctions typées par domaine : `getScans()`, `getFindings()`, `getSources()`, `getRansomLookAlerts()`, `getReports()`, `getUsers()`, etc.
  - Gestion des erreurs 401 → redirect `/login`
  - Hooks React Query (ou SWR) pour chaque ressource

- [x] **0.6 — Guard d'authentification**
  - Middleware Next.js (`middleware.ts`) : vérifier le JWT dans le cookie sur toutes les routes `(dashboard)` et `admin`
  - Redirect `/login` si non authentifié
  - Guard rôle Admin sur les routes `/admin/*`

- [x] **0.7 — Dark/Light mode**
  - Vérifier que `ThemeProvider` est bien en place et fonctionnel
  - Toggle dark/light dans le Header avec persistance (`localStorage`)

---

## PHASE 1 — Dashboard principal (`/`)

> Page `(dashboard)/page.tsx` — déjà partiellement présente, à compléter avec vraies données.

- [x] **1.1 — Graphique d'évolution global (heatmap / barres)**
  - Remplacer les mock data par appel API réel
  - Composant `<FindingsChart />` avec `recharts` ou `chart.js`
  - Filtres temporels fonctionnels (7j / 1 mois / 6 mois / 12 mois)
  - Axes : X = temps, Y = nb findings ; couleurs par sévérité (stacked bars)

- [x] **1.2 — Cards connecteurs / sources**
  - Remplacer les données statiques par API `/api/sources/status`
  - Statut dynamique : ✅ Opérationnel / ⚠️ Dégradé / ❌ Erreur
  - Date du dernier scan réussi
  - Badge CRITICAL si RansomLook a une alerte active

- [x] **1.3 — Bloc alerte RansomLook**
  - Affiché uniquement si une alerte CRITICAL est active
  - Résumé : groupe, date, taille revendiquée, statut
  - CTA → `/alerts/ransomware`

- [x] **1.4 — Tableau des derniers scans**
  - Appel API `/api/scans?limit=10`
  - Colonnes : date, durée, nb findings, sévérité globale
  - Timestamps format `YYYY-MM-DD HH:mm` (sans secondes)
  - Lien vers le détail du scan

- [x] **1.5 — Accès rapide**
  - Liens vers chaque page outil
  - Lien vers la page Rapports

---

## PHASE 2 — Pages par outil (`/tools/*`)

> Une page par source OSINT. Toutes suivent le même layout : TimeFilter + Chart + DataTable.

- [x] **2.1 — Layout partagé `ToolPageLayout`**
  - Composant wrapper réutilisable avec : `<PageHeader />`, `<TimeFilter />`, `<FindingsChart />`, `<DataTable />`, bouton "Relancer un scan" (Admin only)

- [x] **2.2 — Page HIBP & Breaches** (`/tools/hibp`)
  - Graphique d'évolution des fuites emails détectées par HIBP
  - Tableau : date, email (masqué ou tronqué RGPD), nom de la fuite, sévérité
  - Bouton relance scan (Admin)

- [x] **2.3 — Page GitHub & GitLab** (`/tools/github`)
  - Graphique d'évolution des expositions de secrets/code
  - Tableau : date, repo, type (secret / credential / token), sévérité, lien (masqué)
  - Bouton relance scan (Admin)

- [x] **2.4 — Page RansomLook** (`/tools/ransomlook`)
  - Graphique d'alertes détectées dans le temps
  - Tableau : groupe ransomware, victime, date découverte, statut (LISTED/PUBLISHED)
  - Lien CTA vers `/alerts/ransomware` pour le détail

- [x] **2.5 — Page LeakCheck** (`/tools/leakcheck`)
  - Graphique d'évolution fuites LeakCheck
  - Tableau findings avec sévérité

- [x] **2.6 — Page URLScan** (`/tools/urlscan`)
  - Graphique résultats URLScan dans le temps
  - Tableau : date, URL analysée (masquée), score de risque, sévérité

- [ ] **2.7 — Pages supplémentaires** (si API keys configurées)
  - `/tools/dehashed` — Dehashed
  - `/tools/otx` — AlienVault OTX
  - `/tools/intelx` — Intelligence X

---

## PHASE 3 — Page Rapports (`/reports`)

- [x] **3.1 — Liste des rapports**
  - Appel API `/api/reports`
  - Colonnes : date, domaine, sévérité globale, nb emails compromis, alerte ransomware (bool)
  - Pagination côté serveur
  - Filtres : période, sévérité, type (hebdo / manuel)

- [x] **3.2 — Export PDF**
  - Bouton "Exporter PDF" par rapport → `GET /api/reports/{id}/export?format=pdf`
  - Téléchargement direct du fichier

- [x] **3.3 — Export JSON / CSV** (optionnel)
  - Même logique, format alternatif

- [x] **3.4 — Génération de rapport global**
  - Modal : sélecteur de période (date début / date fin)
  - Appel `POST /api/reports/generate` avec la période
  - Feedback spinner + toast succès/erreur

---

## PHASE 4 — Alertes Ransomware (`/alerts/ransomware`)

- [x] **4.1 — Bloc état instance RansomLook**
  - URL utilisée (local ou SaaS), nb groupes suivis, nb posts, dernière mise à jour
  - Appel API `/api/ransomlook/status`

- [x] **4.2 — Liste des alertes**
  - Appel API `/api/ransomlook/alerts`
  - Colonnes : groupe, victime, pays, secteur, claim_size, statut, date découverte, date publication
  - **Jamais d'URL .onion** dans l'interface — indicateur texte uniquement
  - Badges sévérité colorés

- [x] **4.3 — Filtres**
  - Filtrer par : groupe, pays, secteur, statut (LISTED / PUBLISHED)
  - Filtre temporel standard

- [x] **4.4 — Lien rapport**
  - Chaque alerte peut pointer vers le rapport de scan qui la contient

---

## PHASE 5 — Administration (`/admin/*`)

> Toutes ces pages : visible uniquement si `role === "admin"`. Redirect 403 sinon.

- [x] **5.1 — Layout admin**
  - Sous-navigation admin : Utilisateurs / Clés API / SMTP / Scheduling / Audit / **Paramètres**
  - `<AdminGuard />` wrappant toutes les pages `/admin`

- [x] **5.2 — Gestion utilisateurs** (`/admin/users`)
  - Tableau : email, rôle, statut MFA, dernière connexion
  - Actions : créer, désactiver, reset password par email, reset MFA
  - Modal création : email + mot de passe + rôle (Admin/Viewer)
  - Politique de mot de passe affichée : min 16 chars (Admin) / min 12 chars (Viewer)
  - Indicateur rotation mot de passe (date expiration, alerte si dépassée)

- [x] **5.3 — Clés API & Intégrations** (`/admin/api-keys`)
  - Formulaire pour chaque clé : HIBP, GitHub, GitLab, URLScan, OTX, LeakCheck, Dehashed, IntelX, Shodan, Hunter
  - Indicateur visuel : clé présente ✅ / absente ⬜ (jamais en clair)
  - Section RansomLook : toggle local/SaaS + champ API key SaaS
  - Bouton "Tester cette source" → appel santé → toast résultat
  - Champ TARGET_DOMAIN avec sauvegarde

- [x] **5.4 — Configuration SMTP** (`/admin/smtp`)
  - Champs : host, port, TLS/SSL toggle, user, password (masqué), from, reply-to
  - Bouton "Envoyer un mail de test" → feedback toast

- [x] **5.5 — Scheduling** (`/admin/scheduling`)
  - Toggle activation/désactivation du cron
  - Champ expression cron avec validation (affichage lisible : "Tous les lundis à 08:00")
  - Affichage du prochain run prévu
  - Historique des 5 dernières exécutions planifiées

- [x] **5.6 — Audit trail** (`/admin/audit`)
  - Tableau : date, utilisateur, action (login / modif clé / relance scan / export…), IP
  - Filtres : utilisateur, type d'action, période
  - Pagination côté serveur
  - Export CSV de l'audit trail

---

## PHASE 6 — Changelog / Updates (`/changelog`)

- [ ] **6.1 — Page changelog**
  - Liste des versions : numéro, date, résumé des changements
  - Données : fichier statique `CHANGELOG.md` parsé côté serveur (ou API endpoint dédié)
  - Style type timeline verticale

---

## PHASE 7 — Authentification (compléments)

> Page `/login` déjà présente, compléter le parcours.

- [ ] **7.1 — Page login** — vérifier le branchement réel API `/auth/login` (JWT cookie)
- [ ] **7.2 — Page profil utilisateur** (`/profile`)
  - Modifier email / mot de passe
  - Activer / désactiver MFA (QR code TOTP)
  - Afficher rôle, dernière connexion
- [ ] **7.3 — Logout** — appel `POST /auth/logout`, clear cookie JWT, redirect `/login`
- [ ] **7.4 — Page 403 / 404** — pages d'erreur custom cohérentes avec le design

---

## PHASE 8 — Qualité & Tests

- [ ] **8.1 — Tests composants** : tester `SeverityBadge`, `DataTable`, `TimeFilter`, `RadarSpinner`
- [ ] **8.2 — Tests pages** : smoke tests sur toutes les routes principales
- [ ] **8.3 — Accessibilité** : audit `axe-core` ou Lighthouse, focus visible, contrastes
- [ ] **8.4 — Responsive** : vérification mobile 375px sur toutes les pages
- [ ] **8.5 — Storybook** (optionnel) : documenter les composants partagés

---

## PHASE 9 — Alertes CVE / Veille vulnérabilités (`/alerts/cve`)

> Page de surveillance des nouvelles CVE et exploits, alimentée par des sources publiques gratuites.
> Les catégories de surveillance sont configurables par l'admin depuis `/admin/settings` (voir Phase 10).

### Sources gratuites retenues (sans abonnement payant)

| Source | Type | Clé API | URL de base | Filtres disponibles |
|---|---|---|---|---|
| **NVD API 2.0** (NIST) | REST JSON | Optionnelle (rate-limit plus élevé avec clé) | `https://services.nvd.nist.gov/rest/json/cves/2.0` | `keywordSearch`, `cvssV3Severity`, `pubStartDate`, `pubEndDate`, `cpeName` |
| **OSV.dev** (Google) | REST JSON | Aucune | `https://api.osv.dev/v1/query` | Écosystème (npm, PyPI, Go, Maven, RubyGems, NuGet, etc.), package, version |
| **GitHub Advisory Database** | Atom RSS | Aucune | `https://github.com/advisories.atom?query=type%3Areviewed` | Paramètre `query` : écosystème, sévérité, type |
| **CVEFeed.io RSS** | RSS XML | Aucune | `https://cvefeed.io/rssfeed/severity/high.xml` | Severity : `high`, `critical`, `medium` ; aussi `/latest.xml` |

> ⚠️ **NVD sans clé** : limité à 5 requêtes / 30 secondes. **Avec clé** : 50 requêtes / 30 secondes.
> Si `CVE_NVD_API_KEY` est renseignée dans le `.env`, le backend l'utilisera automatiquement.
> Ajouter dans `.env.example` : `CVE_NVD_API_KEY=` (optionnel, laisser vide = mode public)

### Catégories de surveillance disponibles

Basées sur les filtres CPE/keyword de NVD et les écosystèmes OSV :

| Catégorie affichée | Source principale | Filtre appliqué |
|---|---|---|
| **Windows** | NVD | `keywordSearch=Microsoft Windows` |
| **Linux Kernel** | NVD | `keywordSearch=Linux Kernel` |
| **macOS / iOS** | NVD | `keywordSearch=Apple macOS` ou `Apple iOS` |
| **Open Source (npm)** | OSV.dev | `ecosystem=npm` |
| **Open Source (PyPI)** | OSV.dev | `ecosystem=PyPI` |
| **Open Source (Go)** | OSV.dev | `ecosystem=Go` |
| **Open Source (Maven/Java)** | OSV.dev | `ecosystem=Maven` |
| **Open Source (RubyGems)** | OSV.dev | `ecosystem=RubyGems` |
| **Open Source (NuGet/.NET)** | OSV.dev | `ecosystem=NuGet` |
| **GitHub Advisories** | GitHub Atom | Tous types, filtre `reviewed` |
| **CVE Critiques (toutes)** | CVEFeed.io RSS | `/rssfeed/severity/critical.xml` |
| **CVE Hautes (toutes)** | CVEFeed.io RSS | `/rssfeed/severity/high.xml` |

> L'admin peut activer/désactiver chaque catégorie depuis `/admin/settings`.
> Le backend agrège les résultats de toutes les catégories actives et les expose via `/api/cve/alerts`.

### Backend nécessaire

- `GET /api/cve/alerts` — retourne la liste agrégée des CVE récentes selon les catégories actives
  - Paramètres : `severity`, `category`, `limit`, `offset`, `since`
  - Le backend interroge NVD / OSV / GitHub Advisories / CVEFeed selon la config
- `GET /api/cve/settings` — retourne les catégories actives sauvegardées
- `PUT /api/cve/settings` — sauvegarde les catégories sélectionnées par l'admin
- `GET /api/cve/status` — statut de chaque source (dernière mise à jour, nb CVE récupérées)

### Tâches frontend

- [ ] **9.1 — Page `/alerts/cve`**
  - `<PageHeader title="Veille CVE & Exploits" breadcrumb />` avec lien vers `/admin/settings` (Admin only)
  - Bloc statut sources : carte par source (NVD / OSV / GitHub Advisories / CVEFeed) avec `<StatusDot />` + date dernière synchro + nb CVE récupérées — appel `GET /api/cve/status`
  - Filtre catégorie : `<Select multiple />` listant uniquement les catégories activées dans les settings
  - Filtre sévérité : CRITICAL / HIGH / MEDIUM / LOW (multi-select avec badges colorés)
  - `<TimeFilter />` standard (7j / 1 mois / 6 mois / 12 mois / Tout)

- [ ] **9.2 — Tableau des CVE**
  - Appel `GET /api/cve/alerts` avec les filtres actifs
  - Colonnes :
    - **CVE ID** (lien externe vers `https://nvd.nist.gov/vuln/detail/{CVE_ID}`, `target="_blank"`)
    - **Titre / Description** (tronquée à 120 chars + tooltip complet)
    - **Sévérité** (`<SeverityBadge />` : CRITICAL / HIGH / MEDIUM / LOW)
    - **Score CVSS** (format `JetBrains Mono`, coloré selon sévérité)
    - **Catégorie** (badge : Windows / Linux / npm / etc.)
    - **Source** (NVD / OSV / GitHub / CVEFeed)
    - **Date de publication** (format `YYYY-MM-DD`)
  - Tri par date DESC par défaut, tri cliquable sur chaque colonne
  - Pagination côté serveur (25 par page)
  - Bouton "Rafraîchir" → force un re-fetch des sources (Admin only)

- [ ] **9.3 — Graphique d'évolution**
  - `<FindingsChart />` adapté : courbe ou barres empilées par sévérité sur la période sélectionnée
  - Axe X = temps, axe Y = nb CVE publiées
  - Légende : CRITICAL (rouge), HIGH (orange), MEDIUM (jaune), LOW (bleu)

- [ ] **9.4 — Widget "Top CVE critiques du jour"**
  - Bloc latéral ou bandeau en haut de page
  - Liste des 5 dernières CVE CRITICAL publiées (toutes catégories confondues)
  - Rafraîchissement automatique toutes les 15 min côté client (polling ou SSE si dispo)

- [ ] **9.5 — Lien dashboard**
  - Le dashboard (`/`) doit afficher un badge "X nouvelles CVE critiques" avec CTA → `/alerts/cve`
  - Appel `GET /api/cve/alerts?severity=CRITICAL&since=24h&limit=1` pour avoir le count

---

## PHASE 10 — Paramètres de l'instance (`/admin/settings`)

> Page de configuration globale de l'instance BreachRadar, accessible uniquement aux admins.
> Organisée en onglets : **Général** · **Clés API** · **Surveillance CVE** · **Sources custom** · **Notifications** · **Avancé**

- [ ] **10.1 — Section "Surveillance CVE"**
  - Liste des catégories disponibles (voir tableau Phase 9) avec un toggle `<Switch />` par catégorie
  - Regroupement visuel par source : **NVD**, **OSV.dev**, **GitHub Advisories**, **CVEFeed.io**
  - Bouton "Sauvegarder" → `PUT /api/cve/settings` → toast succès/erreur
  - Indicateur : "X catégorie(s) active(s)"
  - Champ optionnel `CVE_NVD_API_KEY` : permet de saisir la clé NVD pour lever le rate-limit
    - Masqué par défaut (type `password`), bouton œil pour révéler
    - Indicateur ✅ / ⬜ selon présence de la clé
    - Sauvegardé via `PUT /api/settings/nvd-key` (jamais renvoyé en clair dans les GET)

- [ ] **10.2 — Section "Général"**
  - Champ `TARGET_DOMAIN` : affichage et édition du domaine cible de l'instance
    - Sauvegardé via `PUT /api/settings/domain`
    - Indication : "Utilisé dans les rapports et la bannière de l'interface"
  - Sélecteur langue par défaut de l'interface (FR / EN)
  - Toggle "Mode maintenance" : affiche une bannière d'avertissement à tous les utilisateurs

- [ ] **10.3 — Section "Notifications"**
  - Toggle activation des alertes email CVE critiques (requiert SMTP configuré)
  - Seuil d'alerte : sélecteur sévérité minimale (CRITICAL only / HIGH+ / MEDIUM+)
  - Champ destinataires : liste d'emails séparés par des virgules
  - Bouton "Envoyer un test" → email de test avec une CVE fictive → toast résultat

- [ ] **10.4 — Section "Avancé"** (optionnel, collapsible)
  - Champ intervalle de polling CVE (en minutes, défaut : 60)
  - Toggle "Inclure les CVE sans score CVSS" (par défaut : désactivé)
  - Bouton "Vider le cache CVE" → `DELETE /api/cve/cache` → confirmation modale + toast

- [ ] **10.5 — Onglet "Clés API"** (`/admin/settings` → onglet *Clés API*)

  > Permet à l'admin de saisir ou remplacer des clés d'API sans redéployer la stack.
  > Ces clés sont stockées **en base de données** (chiffrées au repos) et injectées dans `settings` au runtime.
  > Elles **ne survivent pas** à une suppression du volume Docker (comportement identique à une valeur absente du `.env`).
  > Les valeurs du `.env` restent prioritaires : si une clé est présente dans le `.env` ET en base, c'est la valeur `.env` qui est utilisée.

  **Règles de sécurité strictes (UI) :**
  - ❌ Aucune clé n'est jamais affichée en clair, ni dans un champ, ni dans un retour API
  - L'API ne renvoie qu'un booléen `is_set: true/false` + la date de dernière modification — jamais la valeur
  - Un champ de saisie est **toujours vide** à l'ouverture : taper dedans = remplacer la clé existante
  - Un bouton "Supprimer" efface la valeur en base (ne touche pas au `.env`)

  **Sources couvertes :**

  | Source | Variable correspondante | Gratuit / Payant |
  |---|---|---|
  | HaveIBeenPwned | `HIBP_API_KEY` | Gratuit (clé requise) |
  | GitHub | `GITHUB_TOKEN` | Gratuit |
  | GitLab | `GITLAB_TOKEN` | Gratuit |
  | URLScan.io | `URLSCAN_API_KEY` | Gratuit |
  | AlienVault OTX | `OTX_API_KEY` | Gratuit |
  | LeakCheck.io | `LEAKCHECK_API_KEY` | Payant |
  | Dehashed (email) | `DEHASHED_EMAIL` | Payant |
  | Dehashed (clé) | `DEHASHED_API_KEY` | Payant |
  | Intelligence X | `INTELX_API_KEY` | Payant |
  | Shodan | `SHODAN_API_KEY` | Payant |
  | Hunter.io | `HUNTER_API_KEY` | Payant |
  | RansomLook SaaS | `RANSOMLOOK_SAAS_API_KEY` | Selon plan |
  | NVD (NIST) | `CVE_NVD_API_KEY` | Gratuit (optionnel) |

  **Tâches frontend :**
  - [ ] Grille de cartes par source : nom, icône, statut `is_set` (badge ✅ / ⬜), date MAJ
  - [ ] Chaque carte a deux actions : **"Définir / Remplacer"** (ouvre un `<Dialog>` avec un `<Input type="password" />` + bouton Enregistrer) et **"Supprimer"** (confirmation modale)
  - [ ] Le champ de saisie est toujours vide à l'ouverture du dialog — placeholder : `Nouvelle valeur…`
  - [ ] Bouton "Tester" sur les sources qui supportent un health-check → `POST /api/settings/api-keys/{source}/test` → toast résultat
  - [ ] Avertissement visible : *"Ces clés sont stockées en base de données chiffrée. Elles seront perdues si le volume Docker est supprimé. Pour une persistance garantie, renseignez-les dans votre `.env`."*

  **Backend nécessaire :**
  - Modèle `ApiKeySetting` en base : `source` (enum), `encrypted_value` (chiffré avec Fernet/AES), `updated_at`
  - `GET /api/settings/api-keys` → liste `[{ source, is_set, updated_at }]` — jamais la valeur
  - `PUT /api/settings/api-keys/{source}` → body `{ value: "..." }` — chiffre et stocke
  - `DELETE /api/settings/api-keys/{source}` → supprime l'entrée en base
  - `POST /api/settings/api-keys/{source}/test` → health-check de la source → `{ ok: bool, message: str }`
  - Au démarrage du backend : fusionner `.env` (prioritaire) + valeurs déchiffrées de la base dans `settings`

- [ ] **10.6 — Onglet "Sources custom"** (`/admin/settings` → onglet *Sources custom*)

  > Permet à l'admin d'ajouter des flux RSS/Atom tiers non inclus de base dans BreachRadar.
  > Exemple : flux CERT-FR (`https://www.cert.ssi.gouv.fr/avis/feed/`), BSI, ENISA, ANSSI, flux internes…
  > Les items de ces flux sont normalisés dans le même schéma que les alertes CVE natives et apparaissent dans `/alerts/cve`.

  **Comportement :**
  - L'admin entre une URL de flux RSS/Atom + un nom affiché + une catégorie (ex : `CERT-FR`, `Agences gouvernementales`, libre)
  - Le backend poll ce flux au même intervalle que les sources natives (configurable dans l'onglet *Avancé*)
  - Les items sont parsés avec `feedparser` (Python) et normalisés : `title`, `description`, `link`, `published`, `severity` (défaut : `INFO` si non détectable), `source_name`, `source_type: custom`
  - Ces items apparaissent dans le tableau `/alerts/cve` avec un badge "Source custom" distinctif

  **Flux RSS publics suggérés (pré-remplis en placeholder dans l'UI) :**

  | Organisme | URL du flux |
  |---|---|
  | CERT-FR — Avis | `https://www.cert.ssi.gouv.fr/avis/feed/` |
  | CERT-FR — Alertes | `https://www.cert.ssi.gouv.fr/alerte/feed/` |
  | CERT-FR — Actualités | `https://www.cert.ssi.gouv.fr/actualite/feed/` |
  | ENISA | `https://www.enisa.europa.eu/publications/rss` |
  | US-CERT (CISA Advisories) | `https://www.cisa.gov/uscert/ncas/alerts.xml` |

  **Tâches frontend :**
  - [ ] Tableau des sources custom existantes : nom, URL (tronquée), catégorie, statut dernier poll (`<StatusDot />`), nb items récupérés, date dernière synchro
  - [ ] Bouton "Ajouter une source" → `<Dialog>` avec : champ Nom, champ URL (validation format URL), sélecteur Catégorie (liste libre + suggestions), toggle Activer immédiatement
  - [ ] Actions par ligne : **Activer/Désactiver** (toggle), **Modifier**, **Supprimer** (confirmation modale), **Forcer un poll** → toast résultat
  - [ ] Bouton "Tester l'URL" dans le dialog d'ajout → `POST /api/settings/custom-sources/test` avec l'URL → vérifie que le flux est accessible et parsable, retourne un aperçu des 3 premiers items → affichés dans le dialog avant confirmation
  - [ ] Avertissement si l'URL est en HTTP (non HTTPS) : badge ⚠️ "Flux non sécurisé"
  - [ ] `<EmptyState />` si aucune source custom : message "Aucune source personnalisée" + CTA "Ajouter"

  **Backend nécessaire :**
  - Modèle `CustomFeedSource` en base : `id`, `name`, `url`, `category`, `enabled`, `last_polled_at`, `last_item_count`, `created_at`
  - `GET /api/settings/custom-sources` → liste des sources
  - `POST /api/settings/custom-sources` → créer une source
  - `PUT /api/settings/custom-sources/{id}` → modifier (name, url, category, enabled)
  - `DELETE /api/settings/custom-sources/{id}` → supprimer
  - `POST /api/settings/custom-sources/test` → body `{ url }` → tente de fetcher + parser le flux, retourne `{ ok, title, item_count, preview: [...3 items] }`
  - `POST /api/settings/custom-sources/{id}/poll` → force un re-poll immédiat de la source
  - Le scheduler existant intègre les sources custom `enabled=true` dans son cycle de polling

---

## PHASE 11 — Qualité & Tests (compléments Phases 9 & 10)

- [ ] **11.1** — Tests smoke sur `/alerts/cve` et `/admin/settings`
- [ ] **11.2** — Vérifier le comportement si toutes les catégories CVE sont désactivées → `<EmptyState />` avec CTA vers `/admin/settings`
- [ ] **11.3** — Vérifier le fallback si une source CVE est down (NVD / OSV / CVEFeed) → `<StatusDot status="error" />` + message explicite, les autres sources continuent de fonctionner
- [ ] **11.4** — Tester le rate-limit NVD sans clé : s'assurer que le backend gère le 429 et affiche un avertissement dans le statut de la source
- [ ] **11.5** — Tester la saisie d'une clé API via l'onglet *Clés API* : vérifier qu'elle est bien prise en compte au runtime sans redémarrage, et perdue après suppression du volume
- [ ] **11.6** — Tester l'ajout d'une source custom (ex : CERT-FR) : vérifier que les items apparaissent dans `/alerts/cve` avec le badge "Source custom"
- [ ] **11.7** — Tester le bouton "Tester l'URL" avec une URL invalide, une URL HTTP, et une URL valide

---

## Ordre de développement recommandé

```
Phase 0 (fondations) → Phase 7.1 + 7.3 (auth branchée) → Phase 1 (dashboard réel)
→ Phase 2.1 + 2.2 (HIBP en premier, le plus critique)
→ Phase 4 (RansomLook alertes)
→ Phase 2.3 à 2.7 (autres outils)
→ Phase 3 (rapports)
→ Phase 5 (admin) + Phase 10 (settings) en parallèle
→ Phase 9 (CVE RSS) — dépend de Phase 10 pour les catégories actives
→ Phase 6 + 7.2 + 7.4 (finitions)
→ Phase 8 + 11 (qualité)
```

---

*Dernière mise à jour : 2026-05-13*
