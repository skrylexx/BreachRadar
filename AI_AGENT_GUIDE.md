# AI_AGENT_GUIDE.md — Guide Complet pour Agents IA


> **Dépôt** : BreachRadar — [https://github.com/skrylexx/BreachRadar](https://github.com/skrylexx/BreachRadar)
>
> Ce fichier est le **point d'entrée unique** pour tout agent IA intervenant sur ce projet.
> Il remplace et fusionne : `AGENT.md`, `IA_CHANGE.md` et `READ_BEFORE_RUN_AUDIT.md`.
>
> **Lis ce fichier en entier avant de faire quoi que ce soit.**


***


## 0. Prompt de Reprise Rapide


Copier-coller ce bloc pour démarrer une nouvelle session sur n'importe quel agent IA :


```
Tu reprends le développement du projet BreachRadar.
Lien repo : [https://github.com/skrylexx/BreachRadar](https://github.com/skrylexx/BreachRadar)


Lis le fichier AI_AGENT_GUIDE.md EN ENTIER AVANT de faire quoi que ce soit.
Il contient : ta mission, les protocoles de traçabilité, les règles de passation,
et les instructions de maintenance des fichiers d'audit.


Ensuite, lis dans cet ordre :
1. TECH_STACK.md   — spécifications techniques complètes
2. ROADMAP.md      — état d'avancement exact et prochaine tâche


Respecte scrupuleusement le protocole de traçabilité (section 3 de ce guide) :
documente chaque changement dans ROADMAP.md, mets à jour TECH_STACK.md et
AUDIT_INSTRUCTIONS.md si nécessaire, remplis la section "Prochain Agent" avant
d'atteindre la limite de ta fenêtre de contexte.

Quand une commande shell est nécessaire, privilégie l'utilisation de `rtk` pour
réduire la verbosité et la consommation de tokens sur les commandes longues.
Évite autant que possible les substitutions de commande shell (`$(...)`, backticks)
et préfère des commandes explicites, simples, et découpées en plusieurs étapes.
```


***


## 1. Mission


Contribuer au développement, à la maintenance et à la sécurisation du projet **BreachRadar** — plateforme de veille cyber (Dark Web, ransomware, fuites de données) composée d'un moteur OSINT (CLI) et d'une WebUI (FastAPI + Next.js).


L'objectif est de poser et maintenir des bases **solides, modulaires, sécurisées et parfaitement documentées** pour permettre une collaboration fluide entre agents IA (Claude, Gemini, GPT, etc.) et humain, sans perte d'information entre les sessions.


***


## 2. Fichiers de Référence


### 2.1 — Arborescence des fichiers de pilotage


```
BreachRadar/
├── AI_AGENT_GUIDE.md          ← CE fichier (mission, protocoles, passation, audit)
├── TECH_STACK.md              ← spécifications techniques complètes
├── AUDIT_INSTRUCTIONS.md      ← périmètre et livrables de l'audit sécurité
├── ROADMAP.md                 ← état d'avancement et changelog
├── SECURITY_BEST-PRACTICE.md  ← bonnes pratiques sécurité du projet
└── audit_reports/             ← rapports d'audit archivés (YYYY-MM-DD_<sha>_audit-report.md)
```


### 2.2 — Tableau de référence rapide


| Fichier | Rôle | Mettre à jour quand ? |
|---------|------|-----------------------|
| `AI_AGENT_GUIDE.md` | Mission, protocoles, règles globales, passation | Changement de workflow ou de convention |
| `AUDIT_INSTRUCTIONS.md` | Périmètre et livrables de l'audit | Nouveau composant, faille résolue, nouveau pilier |
| `TECH_STACK.md` | Spécifications techniques complètes | Toute évolution de la stack ou des dépendances |
| `ROADMAP.md` | Avancement, CHANGELOG, prochaine tâche | **À chaque fin de session, sans exception** |
| `audit_reports/` | Rapports d'audit archivés | Après chaque audit sécurité |


### 2.3 — Ordre de lecture selon le type de session


**Session de développement / refactoring :**
```
1. AI_AGENT_GUIDE.md  ← ce fichier (obligatoire, en entier)
2. TECH_STACK.md      ← spécifications techniques
3. ROADMAP.md         ← état d'avancement et prochaine tâche
```


**Session d'audit sécurité :**
```
1. AI_AGENT_GUIDE.md      ← ce fichier (section 8 en particulier)
2. AUDIT_INSTRUCTIONS.md  ← périmètre et livrables de l'audit
3. TECH_STACK.md          ← spécifications techniques complètes
```


> Ne jamais commencer une tâche sans avoir lu au minimum ce fichier + ROADMAP.md.


***


## 3. Livrables Attendus par Type d'Intervention


### 3.1 — Développement (Feature / Fix)


1. **Code** : fichiers sources fonctionnels, propres et commentés selon les priorités du ROADMAP.md
2. **TODO.md** mis à jour :
   - Cocher impérativement (`- [x]`) les cases de TOUTES les étapes terminées jusqu'ici.
3. **ROADMAP.md** mis à jour :
   - Section CHANGELOG : chaque modification listée précisément (fichier, ligne, nature du changement)
   - Indicateur d'avancement mis à jour (ex : `[████░░] 60%`)
   - Section "Prochain agent" complétée si la session s'arrête avant la fin de la tâche
4. **README.md** mis à jour si l'architecture ou les instructions d'installation évoluent


### 3.2 — Audit de Sécurité


1. **Rapport d'audit** archivé dans `audit_reports/YYYY-MM-DD_<sha-court>_audit-report.md`
2. **AUDIT_INSTRUCTIONS.md** mis à jour si nécessaire (voir section 8 ci-dessous)
3. **TECH_STACK.md** mis à jour si nécessaire (voir section 8 ci-dessous)
4. **ROADMAP.md** : ajouter les findings critiques/hauts dans la section "Points de vigilance"


### 3.3 — Refactoring / Infrastructure


1. **Code** refactorisé avec commentaires expliquant les choix
2. **ROADMAP.md** mis à jour avec le CHANGELOG détaillé
3. **TECH_STACK.md** mis à jour si la stack ou l'architecture change
4. **README.md** mis à jour si l'arborescence ou les commandes changent


***


## 4. Protocole de Traçabilité (OBLIGATOIRE)


Chaque intervention doit laisser une trace complète et exploitable par l'agent suivant.


### 4.1 — Avant de commencer


- Lire ROADMAP.md pour connaître l'état exact du projet
- Identifier le dernier commit audité dans TECH_STACK.md
- Comparer avec le HEAD actuel : `git log --oneline -10`
- Si des fichiers critiques ont changé depuis la dernière session, mettre à jour TECH_STACK.md avant de commencer
- Vérifier si `rtk` est disponible dans l'environnement avant d'exécuter des commandes shell verbeuses


### 4.2 — Pendant l'intervention


Tout changement effectué doit être documenté **immédiatement** dans ROADMAP.md selon le format suivant :


```markdown
### [YYYY-MM-DD] — <Titre court de l'action>
- **Fichier(s) modifié(s)** : `chemin/vers/fichier.py` (lignes X-Y)
- **Nature** : [Ajout | Modification | Suppression | Refactoring | Fix | Sécurité]
- **Raison** : Explication concise du pourquoi
- **Impact** : Modules ou comportements affectés
- **Commit** : `<SHA>` (si applicable)
```


### 4.3 — Gestion des Tokens & Arrêt Préventif


- **Seuil d'alerte** : à ~80% de la fenêtre de contexte, arrêter d'écrire du code
- **Action obligatoire avant arrêt** : consacrer les derniers tokens à mettre à jour ROADMAP.md avec :
  - Ce qui a été fait dans la session
  - Ce qui reste à faire (avec fichiers et fonctions précis)
  - Les points de vigilance pour l'agent suivant
  - Le SHA du dernier commit de la session
- **Format de la section "Prochain agent"** dans ROADMAP.md :


```markdown
## 🤖 Prochain Agent — Reprendre ici


**Arrêté à** : `chemin/vers/fichier.py` — fonction `nom_fonction()`, ligne X
**Commit** : `<SHA>`
**Ce qui reste** :
- [ ] Tâche 1 (fichier cible : `...`)
- [ ] Tâche 2 (fichier cible : `...`)
**Points de vigilance** :
- Point 1
- Point 2
```


### 4.4 — Interopérabilité entre agents


- Utiliser des **commentaires explicites** dans le code : `# TODO(agent): ...`, `# NOTE: ...`, `# SECURITY: ...`
- Ne jamais laisser de code incomplet sans commentaire signalant l'état : `# WIP: implémentation partielle — voir ROADMAP.md`
- Toujours préciser dans ROADMAP.md quel agent a travaillé sur quelle section


### 4.5 — Politique Shell / RTK


- Quand une commande shell est nécessaire, **préférer `rtk`** pour les commandes potentiellement longues ou verbeuses (`git status`, `git diff`, `docker ps`, `pytest`, `npm`, `pnpm`, `ls`, `find`, etc.).
- Si `rtk` est disponible, privilégier par défaut des formes comme `rtk git status`, `rtk git diff`, `rtk pytest`, `rtk docker ps`.
- Éviter autant que possible les substitutions de commande shell :
  - `$(...)`
  - backticks
  - commandes imbriquées complexes dans un seul appel
- Préférer des commandes simples, explicites, et découpées en plusieurs étapes plutôt qu'une seule ligne difficile à auditer.
- Si une substitution semble nécessaire, chercher d'abord une alternative sans substitution.
- Ne pas supposer que `rtk` est disponible sur tous les environnements : vérifier sa présence, puis fallback sur une commande standard si absent.


***


## 5. Protocole de Passation Inter-Agents


### 5.1 — Ce que l'agent sortant DOIT faire avant de clore sa session


- [ ] Mettre à jour **ROADMAP.md** : CHANGELOG de la session + section `Prochain Agent — Reprendre ici`
- [ ] Mettre à jour **TECH_STACK.md** si la stack a évolué (nouvelles dépendances, services, secrets)
- [ ] Mettre à jour **AUDIT_INSTRUCTIONS.md** si de nouveaux composants ont été ajoutés
- [ ] Ajouter une entrée dans la section **6. Historique des Passations** ci-dessous
- [ ] Pousser un commit avec le message : `docs: mise à jour ROADMAP + AI_AGENT_GUIDE [fin session <agent>]`


### 5.2 — Ce que l'agent entrant DOIT faire avant de commencer


- [ ] Lire ce fichier en entier
- [ ] Lire les fichiers de référence dans l'ordre indiqué en section 2.3
- [ ] Vérifier le dernier commit audité dans TECH_STACK.md vs HEAD actuel
- [ ] Consulter la section `Prochain Agent — Reprendre ici` dans ROADMAP.md
- [ ] Ne pas modifier de code avant d'avoir lu ces fichiers


### 5.3 — Format d'une entrée de passation


```
### Passation #N — YYYY-MM-DD
- **Agent sortant**           : [Claude / Gemini / GPT-4 / autre]
- **Agent entrant**           : [Claude / Gemini / GPT-4 / autre — ou "indéfini"]
- **Commit de fin de session**: <SHA>
- **Tâches accomplies**       :
  - Résumé bref des actions effectuées
- **Tâche suivante**          : Description précise + fichier cible
- **Points de vigilance**     :
  - Point 1
  - Point 2
- **Fichiers mis à jour**     : ROADMAP.md | TECH_STACK.md | AUDIT_INSTRUCTIONS.md
```


***


## 6. Historique des Passations


### Passation #1 — 2026-05-04


- **Agent sortant**            : Claude (Perplexity — session initiale de structuration)
- **Agent entrant**            : indéfini
- **Commit de fin de session** : `08508ac`
- **Tâches accomplies** :
  - Architecture complète en place (backend FastAPI + frontend Next.js + Docker Compose)
  - Création et structuration de tous les fichiers de pilotage :
    `AGENT.md`, `READ_BEFORE_RUN_AUDIT.md`, `AUDIT_INSTRUCTIONS.md`, `TECH_STACK.md`, `IA_CHANGE.md`
- **Tâche suivante** : Voir section `Prochain Agent — Reprendre ici` dans ROADMAP.md
- **Points de vigilance** :
  - `/auth/mfa/verify` retourne `501 NOT_IMPLEMENTED` — MFA non fonctionnel en l'état
  - `curl | sh` dans `backend/Dockerfile` — risque supply chain (aucune vérification d'intégrité)
  - Images Docker `dperson/torproxy:latest` et `travishunting/ransomlook:latest` non épinglées
  - CSP avec `unsafe-eval` + `unsafe-inline` dans `frontend/next.config.ts`
  - `UI_REDIS_PASSWORD` visible dans la commande `redis-server` (docker inspect / ps aux)
- **Fichiers mis à jour** : AGENT.md · TECH_STACK.md · AUDIT_INSTRUCTIONS.md · READ_BEFORE_RUN_AUDIT.md · IA_CHANGE.md


### Passation #2 — 2026-05-05


- **Agent sortant**            : Claude (Perplexity — session refactoring documentation + UI)
- **Agent entrant**            : Gemini (session de construction Backend)
- **Commit de fin de session** : *(voir commit associé à ce push)*
- **Tâches accomplies** :
  - Fusion de `AGENT.md`, `IA_CHANGE.md`, `READ_BEFORE_RUN_AUDIT.md` → `AI_AGENT_GUIDE.md`
  - Correction du logo dans `Sidebar.tsx` (remplacement de l'icône Shield par `images/logo_nobg.png`)
  - Ajout du composant `DomainBanner.tsx` affichant le domaine cible (`NEXT_PUBLIC_TARGET_DOMAIN`)
  - Intégration de la bannière dans `frontend/src/app/(dashboard)/layout.tsx`
- **Tâche suivante** : Voir section `Prochain Agent — Reprendre ici` dans ROADMAP.md
- **Points de vigilance** : Mêmes points de vigilance sécurité que la passation #1 (non résolus)
- **Fichiers mis à jour** : AI_AGENT_GUIDE.md (nouveau) · Sidebar.tsx · layout.tsx (dashboard) · DomainBanner.tsx (nouveau)


***


### Passation #3 — 2026-05-15


- **Agent sortant**            : Gemini (session de construction Backend)
- **Agent entrant**            : indéfini
- **Commit de fin de session** : *(voir commit associé à ce push)*
- **Tâches accomplies** :
  - Architecture Backend posée : Modèles SQLAlchemy (CVE, Settings, API Keys).
  - Sécurité : Implémentation du chiffrement Fernet pour les secrets en base.
  - Moteur CVE : Fetchers NVD API 2.0, GitHub, CVEFeed et gestion du rate-limit.
  - Système Mock Data : Génération dynamique de données de démo si clés absentes.
  - UI : Switch MOCK global, bannières d'avertissement et badges sur tout le dashboard.
- **Tâche suivante** : Implémentation du polling réel et finalisation du fetcher OSV.dev.
- **Points de vigilance** :
  - Clé NVD recommandée pour éviter le rate-limit strict (5 req/30s).
  - Les boutons MFA et Password dans Profile sont visuels mais pas encore reliés au backend.
- **Fichiers mis à jour** : TODO.md · ROADMAP.md · README.md · QUICKSTART.md · Tout le backend/app/...


### Passation #4 — 2026-05-18


- **Agent sortant**            : Gemini CLI
- **Agent entrant**            : indéfini
- **Commit de fin de session** : *(voir commit associé à ce push)*
- **Tâches accomplies** :
  - Génération de la documentation technique complète pour les sous-dossiers.
  - Création de `backend/README.md` (FastAPI, Endpoints, Local Setup).
  - Création de `frontend/README.md` (Next.js, Tech stack, Local Setup).
  - Mise à jour majeure de `QUICKSTART.md` pour inclure le guide de développement local (sans Docker).
  - Mise à jour du `ROADMAP.md` (Phase 5 Hardening marquée à 100%).
- **Tâche suivante** : Voir section `Prochain Agent — Reprendre ici` dans ROADMAP.md (Focus sur le polling CVE réel et les actions profil).
- **Points de vigilance** :
  - Le guide local suppose que PostgreSQL et Redis sont accessibles nativement ou via des conteneurs isolés.
  - Vérifier la cohérence du `.env` lors du switch Docker <-> Local.
- **Fichiers mis à jour** : backend/README.md · frontend/README.md · QUICKSTART.md · ROADMAP.md · AI_AGENT_GUIDE.md


### Passation #5 — 2026-05-18

- **Agent sortant**            : Gemini CLI
- **Agent entrant**            : indéfini
- **Commit de fin de session** : *(voir commit associé à ce push)*
- **Tâches accomplies** :
  - Création du fichier `ARCHITECTURE.md` détaillant la structure du repo, les configs et les fichiers IA.
  - Mise à jour du `ROADMAP.md` (Itération 23).
- **Tâche suivante** : Reprendre le développement backend (polling CVE, actions profil) comme indiqué dans la ROADMAP.
- **Points de vigilance** : Aucun nouveau point de vigilance technique introduit par cette itération de documentation.
- **Fichiers mis à jour** : ARCHITECTURE.md · ROADMAP.md · AI_AGENT_GUIDE.md


### Passation #7 — 2026-05-23

- **Agent sortant**            : Gemini CLI
- **Agent entrant**            : indéfini
- **Commit de fin de session** : `77a21a7` (base) + v0.2.3
- **Tâches accomplies** :
  - **Refonte MFA & Session** : Fix logout prématuré, ajout backup codes, mode secours, auto-focus UX.
  - **Veille Numérique (v0.2.3)** :
    - Implémentation du moteur `IntelligenceMonitor` (RSS, GitHub, Pastebin stub).
    - Système d'alerting `CRITICAL` via Webhook/Email intégré au collecteur.
    - Interface `/intelligence` avec filtres dynamiques (Sévérité, Lu/Non-lu).
    - Ajout de 5 sources cyber majeures dont IT-Connect.
  - Diagnostic et correction du crash backend lié au schéma DB (migration SQL effectuée).
  - Validation de l'ensemble de la stack Docker (tous les services sont healthy).
- **Tâche suivante** : Liaison NotificationEngine avancée (Templating) et actions de masse sur le Feed.
- **Points de vigilance** :
  - Le `cyber_findings.extra_metadata` est un JSONB flexible, idéal pour stocker les spécificités de chaque source.
  - Le dédoublonnage est basé sur un hash SHA256 de l'URL/external_id.
- **Fichiers mis à jour** : ROADMAP.md · AI_AGENT_GUIDE.md · README.md · TODO.md · changelog/page.tsx

***

### Passation #6 — 2026-05-21

- **Agent sortant**            : Gemini CLI
- **Agent entrant**            : indéfini
- **Commit de fin de session** : `92c060f`
- **Tâches accomplies** :
  - Analyse complète de l'implémentation MFA actuelle (Backend auth.py & Frontend login page).
  - Création d'une roadmap d'implémentation détaillée dans `TODO.md` (MFA flow, Admin controls, Hardening).
- **Tâche suivante** : Implémenter la page `/mfa` dans le frontend et mettre à jour le middleware pour autoriser son accès (voir `TODO.md`).
- **Points de vigilance** :
  - Le middleware Next.js redirige vers `/login` si `access_token` est absent, ce qui bloque `/mfa`.
  - Le schéma `MFAVerifyRequest` côté backend ne contient pas d'identifiant utilisateur (nécessite email ou scan Redis du challenge token).
- **Fichiers mis à jour** : TODO.md · ROADMAP.md · AI_AGENT_GUIDE.md


***


## 7. Instructions de Style & Qualité


- **Précision technique maximale** — zéro généralité, zéro approximation
- **Code propre, commenté et modulaire** — chaque fonction a une docstring, chaque module a un commentaire d'en-tête
- **Pas de blabla inutile** — se concentrer sur l'exécution et le suivi de l'avancement
- **Tests obligatoires** pour tout nouveau code métier : pytest + pytest-asyncio
- **Linting avant commit** : `ruff check .` et `mypy` ne doivent retourner aucune erreur bloquante
- **Secrets** : ne jamais hardcoder de valeur sensible — toujours passer par `settings` (pydantic-settings)
- **Pas de `print()`** en production — utiliser le logger configuré dans `main.py`
- **Favoriser `rtk`** pour réduire la sortie inutile des commandes shell quand l'outil est disponible
- **Éviter les substitutions shell** quand une alternative explicite existe


***


## 8. Maintenance des Fichiers d'Audit (Avant Tout Run d'Audit)


> Cette section remplace `READ_BEFORE_RUN_AUDIT.md`. À lire avant toute session d'audit sécurité.


### 8.1 — Vérification préalable au run


Avant de lancer l'audit, effectuer les vérifications suivantes.


**Comparer le commit actuel avec le dernier commit audité :**


Récupérer le SHA du dernier commit audité dans `TECH_STACK.md` (champ `Dernier commit audité`).
Comparer avec le HEAD actuel du dépôt via :


```bash
git log --oneline -20
git diff <sha_dernier_audit> HEAD --name-only
```


Si des fichiers ont changé depuis le dernier audit, passer à l'étape suivante.
Si aucun changement, l'audit peut démarrer directement.


**Classifier les fichiers modifiés selon leur impact :**


| Fichier modifié | Action requise |
|-----------------|----------------|
| `backend/app/routers/*.py` | Mettre à jour section 1.2 de `AUDIT_INSTRUCTIONS.md` + section 2 de `TECH_STACK.md` |
| `backend/app/core/config.py` | Mettre à jour sections Secrets et Backend de `TECH_STACK.md` |
| `backend/app/core/security.py` | Mettre à jour section 1.1 de `AUDIT_INSTRUCTIONS.md` |
| `backend/pyproject.toml` | Mettre à jour les dépendances dans `TECH_STACK.md` section 2 |
| `frontend/package.json` | Mettre à jour les dépendances dans `TECH_STACK.md` section 3 |
| `frontend/next.config.ts` | Mettre à jour section 3 de `TECH_STACK.md` (headers CSP) |
| `docker-compose.yml` | Mettre à jour section 4 de `TECH_STACK.md` |
| `backend/Dockerfile` ou `frontend/Dockerfile` | Mettre à jour section 4 de `TECH_STACK.md` |
| `backend/app/engine/logic.py` | Mettre à jour section 1.6 de `AUDIT_INSTRUCTIONS.md` |
| `backend/app/clients/` | Mettre à jour section 6 de `TECH_STACK.md` (sources OSINT) |
| `.env.example` | Mettre à jour section 5 de `TECH_STACK.md` (secrets) |


### 8.2 — Quand mettre à jour TECH_STACK.md


Mettre à jour `TECH_STACK.md` **obligatoirement** si l'une des conditions suivantes est remplie :


| Condition | Section à mettre à jour |
|-----------|--------------------------|
| Nouvelle dépendance dans `pyproject.toml` ou `package.json` | Section 2 (Backend) ou 3 (Frontend) |
| Changement de version d'une dépendance existante | Section correspondante + vérifier CVE |
| Nouveau service dans `docker-compose.yml` | Section 4 (Conteneurisation) |
| Nouvelle variable dans `.env.example` | Section 5 (Secrets) |
| Nouvelle source OSINT dans `sources.yaml` ou `clients/` | Section 6 (Sources OSINT) |
| Nouveau router ou module dans `backend/app/` | Section 2 (Backend) + Section 8 (Fichiers clés) |
| Changement d'image Docker de base | Section 4 (Conteneurisation) |


Après mise à jour, actualiser le champ :
```
Dernier commit audité : <SHA>
Date de mise à jour   : YYYY-MM-DD
```


### 8.3 — Quand mettre à jour AUDIT_INSTRUCTIONS.md


Mettre à jour `AUDIT_INSTRUCTIONS.md` **obligatoirement** si l'une des conditions suivantes est remplie :


| Condition | Action |
|-----------|--------|
| Nouveau fichier dans `backend/app/routers/` | Ajouter dans les fichiers cibles du pilier concerné |
| Nouvelle fonctionnalité critique (SSO, export, import, nouveau rôle) | Ajouter les points d'analyse dans le pilier pertinent |
| Faille documentée résolue | Marquer `[RÉSOLU - commit <SHA>]` puis archiver |
| Changement d'infrastructure (Nginx, Kubernetes, reverse proxy...) | Mettre à jour le pilier 1.4 |
| Nouvel endpoint d'authentification | Mettre à jour le pilier 1.1 |


**Règle d'or** : ne jamais supprimer un point d'analyse sans l'avoir marqué `[RÉSOLU]` avec le SHA du commit de correction.


### 8.4 — Archivage des rapports d'audit


Chaque rapport d'audit produit doit être sauvegardé selon la convention suivante :


```
audit_reports/
└── YYYY-MM-DD_<sha-court>_audit-report.md
```


Exemple : `audit_reports/2026-05-04_a3f9c12_audit-report.md`


Le rapport doit inclure en en-tête :


```
Commit audité  : <SHA complet>
Date d'audit   : YYYY-MM-DD
Auditeur       : [Nom / Outil IA]
Fichiers lus   : TECH_STACK.md, AUDIT_INSTRUCTIONS.md (versions du jour)
```


### 8.5 — Contrôle de cohérence finale (fin de session d'audit)


- [ ] `TECH_STACK.md` reflète l'état actuel du dépôt (pas de dépendance manquante, pas de service non documenté)
- [ ] `AUDIT_INSTRUCTIONS.md` covers all active files and components of the repository
- [ ] The field `Dernier commit audité` in `TECH_STACK.md` is up to date
- [ ] The audit report is archived in `audit_reports/` with the naming convention
- [ ] Fixed vulnerabilities since the last audit have been removed or marked `[RÉSOLU]` in `AUDIT_INSTRUCTIONS.md`
- [ ] No sensitive information (API key, password, token) appears in clear text in the documentation files