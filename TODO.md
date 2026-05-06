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
| `/scans` | — | ❌ Inexistant |
| `/tools/hibp` | — | ❌ Inexistant |
| `/tools/github` | — | ❌ Inexistant |
| `/tools/ransomlook` | — | ❌ Inexistant |
| `/tools/leakcheck` | — | ❌ Inexistant |
| `/tools/urlscan` | — | ❌ Inexistant |
| `/reports` | — | ❌ Inexistant |
| `/alerts/ransomware` | — | ❌ Inexistant |
| `/admin/users` | — | ❌ Inexistant |
| `/admin/api-keys` | — | ❌ Inexistant |
| `/admin/smtp` | — | ❌ Inexistant |
| `/admin/scheduling` | — | ❌ Inexistant |
| `/admin/audit` | — | ❌ Inexistant |
| `/changelog` | — | ❌ Inexistant |
| `/profile` | — | ❌ Inexistant |
| `/cve-rss` | - | ❌ Inexistant |

---

## PHASE 0 — Fondations & Infrastructure UI

> Prérequis à toutes les pages. À faire en premier.

- [ ] **0.1 — Design system tokens**
  - Vérifier / compléter `globals.css` : variables CSS pour les couleurs de sévérité (`--color-critical`, `--color-high`, `--color-medium`, `--color-low`)
  - Palette dark-first conforme au CDC : fond `#09090b`, surfaces `#18181b`, accent `#38bdf8`
  - Police `Inter` (UI) + `JetBrains Mono` (données techniques) via `next/font`

- [ ] **0.2 — Composants Shadcn/UI manquants**
  - Installer : `badge`, `table`, `tabs`, `select`, `dialog`, `toast`, `skeleton`, `tooltip`, `switch`, `form`, `input`, `label`, `separator`, `dropdown-menu`, `alert`, `progress`
  - Vérifier que `button`, `card` sont déjà présents

- [ ] **0.3 — Composants partagés custom**
  - `<SeverityBadge level="CRITICAL|HIGH|MEDIUM|LOW" />` — badge coloré réutilisable
  - `<StatusDot status="ok|warning|error" />` — indicateur de statut source
  - `<PageHeader title props breadcrumb />` — en-tête de page standard
  - `<EmptyState icon message action />` — état vide standard
  - `<DataTable columns data pagination />` — tableau paginé réutilisable (wrapper Tanstack Table ou Shadcn)
  - `<RadarSpinner />` — spinner animé type radar (SVG, utilisé pendant les scans)
  - `<TimeFilter value onChange />` — sélecteur 7j / 1 mois / 6 mois / 12 mois / Tout

- [ ] **0.4 — i18n setup**
  - Installer et configurer `next-intl` (ou `next-i18next`)
  - Créer `messages/en.json` et `messages/fr.json` avec les clés de base
  - Ajouter le sélecteur langue dans le Header (icône globe + EN/FR)
  - Stocker la préférence en `localStorage` / cookie

- [ ] **0.5 — Couche API client**
  - Créer `frontend/src/lib/api.ts` : client HTTP centralisé (fetch avec `NEXT_PUBLIC_API_URL`)
  - Fonctions typées par domaine : `getScans()`, `getFindings()`, `getSources()`, `getRansomLookAlerts()`, `getReports()`, `getUsers()`, etc.
  - Gestion des erreurs 401 → redirect `/login`
  - Hooks React Query (ou SWR) pour chaque ressource

- [ ] **0.6 — Guard d'authentification**
  - Middleware Next.js (`middleware.ts`) : vérifier le JWT dans le cookie sur toutes les routes `(dashboard)` et `admin`
  - Redirect `/login` si non authentifié
  - Guard rôle Admin sur les routes `/admin/*`

- [ ] **0.7 — Dark/Light mode**
  - Vérifier que `ThemeProvider` est bien en place et fonctionnel
  - Toggle dark/light dans le Header avec persistance (`localStorage`)

---

## PHASE 1 — Dashboard principal (`/`)

> Page `(dashboard)/page.tsx` — déjà partiellement présente, à compléter avec vraies données.

- [ ] **1.1 — Graphique d'évolution global (heatmap / barres)**
  - Remplacer les mock data par appel API réel
  - Composant `<FindingsChart />` avec `recharts` ou `chart.js`
  - Filtres temporels fonctionnels (7j / 1 mois / 6 mois / 12 mois)
  - Axes : X = temps, Y = nb findings ; couleurs par sévérité (stacked bars)

- [ ] **1.2 — Cards connecteurs / sources**
  - Remplacer les données statiques par API `/api/sources/status`
  - Statut dynamique : ✅ Opérationnel / ⚠️ Dégradé / ❌ Erreur
  - Date du dernier scan réussi
  - Badge CRITICAL si RansomLook a une alerte active

- [ ] **1.3 — Bloc alerte RansomLook**
  - Affiché uniquement si une alerte CRITICAL est active
  - Résumé : groupe, date, taille revendiquée, statut
  - CTA → `/alerts/ransomware`

- [ ] **1.4 — Tableau des derniers scans**
  - Appel API `/api/scans?limit=10`
  - Colonnes : date, durée, nb findings, sévérité globale
  - Timestamps format `YYYY-MM-DD HH:mm` (sans secondes)
  - Lien vers le détail du scan

- [ ] **1.5 — Accès rapide**
  - Liens vers chaque page outil
  - Lien vers la page Rapports

---

## PHASE 2 — Pages par outil (`/tools/*`)

> Une page par source OSINT. Toutes suivent le même layout : TimeFilter + Chart + DataTable.

- [ ] **2.1 — Layout partagé `ToolPageLayout`**
  - Composant wrapper réutilisable avec : `<PageHeader />`, `<TimeFilter />`, `<FindingsChart />`, `<DataTable />`, bouton "Relancer un scan" (Admin only)

- [ ] **2.2 — Page HIBP & Breaches** (`/tools/hibp`)
  - Graphique d'évolution des fuites emails détectées par HIBP
  - Tableau : date, email (masqué ou tronqué RGPD), nom de la fuite, sévérité
  - Bouton relance scan (Admin)

- [ ] **2.3 — Page GitHub & GitLab** (`/tools/github`)
  - Graphique d'évolution des expositions de secrets/code
  - Tableau : date, repo, type (secret / credential / token), sévérité, lien (masqué)
  - Bouton relance scan (Admin)

- [ ] **2.4 — Page RansomLook** (`/tools/ransomlook`)
  - Graphique d'alertes détectées dans le temps
  - Tableau : groupe ransomware, victime, date découverte, statut (LISTED/PUBLISHED)
  - Lien CTA vers `/alerts/ransomware` pour le détail

- [ ] **2.5 — Page LeakCheck** (`/tools/leakcheck`)
  - Graphique d'évolution fuites LeakCheck
  - Tableau findings avec sévérité

- [ ] **2.6 — Page URLScan** (`/tools/urlscan`)
  - Graphique résultats URLScan dans le temps
  - Tableau : date, URL analysée (masquée), score de risque, sévérité

- [ ] **2.7 — Pages supplémentaires** (si API keys configurées)
  - `/tools/dehashed` — Dehashed
  - `/tools/otx` — AlienVault OTX
  - `/tools/intelx` — Intelligence X

---

## PHASE 3 — Page Rapports (`/reports`)

- [ ] **3.1 — Liste des rapports**
  - Appel API `/api/reports`
  - Colonnes : date, domaine, sévérité globale, nb emails compromis, alerte ransomware (bool)
  - Pagination côté serveur
  - Filtres : période, sévérité, type (hebdo / manuel)

- [ ] **3.2 — Export PDF**
  - Bouton "Exporter PDF" par rapport → `GET /api/reports/{id}/export?format=pdf`
  - Téléchargement direct du fichier

- [ ] **3.3 — Export JSON / CSV** (optionnel)
  - Même logique, format alternatif

- [ ] **3.4 — Génération de rapport global**
  - Modal : sélecteur de période (date début / date fin)
  - Appel `POST /api/reports/generate` avec la période
  - Feedback spinner + toast succès/erreur

---

## PHASE 4 — Alertes Ransomware (`/alerts/ransomware`)

- [ ] **4.1 — Bloc état instance RansomLook**
  - URL utilisée (local ou SaaS), nb groupes suivis, nb posts, dernière mise à jour
  - Appel API `/api/ransomlook/status`

- [ ] **4.2 — Liste des alertes**
  - Appel API `/api/ransomlook/alerts`
  - Colonnes : groupe, victime, pays, secteur, claim_size, statut, date découverte, date publication
  - **Jamais d'URL .onion** dans l'interface — indicateur texte uniquement
  - Badges sévérité colorés

- [ ] **4.3 — Filtres**
  - Filtrer par : groupe, pays, secteur, statut (LISTED / PUBLISHED)
  - Filtre temporel standard

- [ ] **4.4 — Lien rapport**
  - Chaque alerte peut pointer vers le rapport de scan qui la contient

---

## PHASE 5 — Administration (`/admin/*`)

> Toutes ces pages : visible uniquement si `role === "admin"`. Redirect 403 sinon.

- [ ] **5.1 — Layout admin**
  - Sous-navigation admin : Utilisateurs / Clés API / SMTP / Scheduling / Audit
  - `<AdminGuard />` wrappant toutes les pages `/admin`

- [ ] **5.2 — Gestion utilisateurs** (`/admin/users`)
  - Tableau : email, rôle, statut MFA, dernière connexion
  - Actions : créer, désactiver, reset password par email, reset MFA
  - Modal création : email + mot de passe + rôle (Admin/Viewer)
  - Politique de mot de passe affichée : min 16 chars (Admin) / min 12 chars (Viewer)
  - Indicateur rotation mot de passe (date expiration, alerte si dépassée)

- [ ] **5.3 — Clés API & Intégrations** (`/admin/api-keys`)
  - Formulaire pour chaque clé : HIBP, GitHub, GitLab, URLScan, OTX, LeakCheck, Dehashed, IntelX, Shodan, Hunter
  - Indicateur visuel : clé présente ✅ / absente ⬜ (jamais en clair)
  - Section RansomLook : toggle local/SaaS + champ API key SaaS
  - Bouton "Tester cette source" → appel santé → toast résultat
  - Champ TARGET_DOMAIN avec sauvegarde

- [ ] **5.4 — Configuration SMTP** (`/admin/smtp`)
  - Champs : host, port, TLS/SSL toggle, user, password (masqué), from, reply-to
  - Bouton "Envoyer un mail de test" → feedback toast

- [ ] **5.5 — Scheduling** (`/admin/scheduling`)
  - Toggle activation/désactivation du cron
  - Champ expression cron avec validation (affichage lisible : "Tous les lundis à 08:00")
  - Affichage du prochain run prévu
  - Historique des 5 dernières exécutions planifiées

- [ ] **5.6 — Audit trail** (`/admin/audit`)
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

## Ordre de développement recommandé

```
Phase 0 (fondations) → Phase 7.1 + 7.3 (auth branchée) → Phase 1 (dashboard réel)
→ Phase 2.1 + 2.2 (HIBP en premier, le plus critique)
→ Phase 4 (RansomLook alertes)
→ Phase 2.3 à 2.7 (autres outils)
→ Phase 3 (rapports)
→ Phase 5 (admin)
→ Phase 6 + 7.2 + 7.4 (finitions)
→ Phase 8 (qualité)
```

---

*Dernière mise à jour : 2026-05-05*
