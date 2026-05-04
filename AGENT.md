# AGENT.md — Instructions Générales pour Agents IA
> Dépôt : BreachRadar — https://github.com/skrylexx/BreachRadar
> Ce fichier est lu **en premier** par tout agent IA intervenant sur ce projet.
> Il définit la mission, les protocoles de travail, les livrables attendus et les règles de traçabilité.

***

## 0. Fichiers de Référence & Ordre de Lecture

Avant toute intervention, lire les fichiers suivants dans cet ordre :

```
1. AGENT.md                  ← ce fichier (mission, protocoles, règles)
2. READ_BEFORE_RUN.md        ← vérification et maintenance des fichiers d'audit
3. AUDIT_INSTRUCTIONS.md     ← périmètre, livrables et règles d'audit sécurité
4. TECH_STACK.md             ← spécifications techniques complètes du projet
5. ROADMAP.md                ← état d'avancement, changelog, prochaines étapes
```

Ne jamais commencer une tâche sans avoir lu au minimum les fichiers 1 et 5 (AGENT.md + ROADMAP.md).
Pour toute tâche touchant à la sécurité, lire également les fichiers 2, 3 et 4.

***

## 1. Mission

Contribuer au développement, à la maintenance et à la sécurisation du projet **BreachRadar** — plateforme de veille cyber (Dark Web, ransomware, fuites de données) composée d'un moteur OSINT (CLI) et d'une WebUI (FastAPI + Next.js).

L'objectif est de poser et maintenir des bases **solides, modulaires, sécurisées et parfaitement documentées** pour permettre une collaboration fluide entre agents IA (Claude, Gemini, GPT, etc.) et humain, sans perte d'information entre les sessions.

***

## 2. Livrables Attendus par Type d'Intervention

### 2.1 — Développement (Feature / Fix)

1. **Code** : fichiers sources fonctionnels, propres et commentés selon les priorités du ROADMAP.md
2. **ROADMAP.md** mis à jour :
   - Section CHANGELOG : chaque modification listée précisément (fichier, ligne, nature du changement)
   - Indicateur d'avancement mis à jour (ex : `[████░░] 60%`)
   - Section "Prochain agent" complétée si la session s'arrête avant la fin de la tâche
3. **README.md** mis à jour si l'architecture ou les instructions d'installation évoluent

### 2.2 — Audit de Sécurité

1. **Rapport d'audit** archivé dans `audits_reports/YYYY-MM-DD_<sha-court>_audit-report.md`
2. **AUDIT_INSTRUCTIONS.md** mis à jour si nécessaire (voir section 4 ci-dessous)
3. **TECH_STACK.md** mis à jour si nécessaire (voir section 4 ci-dessous)
4. **ROADMAP.md** : ajouter les findings critiques/hauts dans la section "Points de vigilance"

### 2.3 — Refactoring / Infrastructure

1. **Code** refactorisé avec commentaires expliquant les choix
2. **ROADMAP.md** mis à jour avec le CHANGELOG détaillé
3. **TECH_STACK.md** mis à jour si la stack ou l'architecture change
4. **README.md** mis à jour si l'arborescence ou les commandes changent

***

## 3. Protocole de Traçabilité (OBLIGATOIRE)

Chaque intervention doit laisser une trace complète et exploitable par l'agent suivant.

### 3.1 — Avant de commencer

- Lire ROADMAP.md pour connaître l'état exact du projet
- Identifier le dernier commit audité dans TECH_STACK.md
- Comparer avec le HEAD actuel : `git log --oneline -10`
- Si des fichiers critiques ont changé depuis la dernière session, mettre à jour TECH_STACK.md avant de commencer

### 3.2 — Pendant l'intervention

Tout changement effectué doit être documenté **immédiatement** dans ROADMAP.md selon le format suivant :

```markdown
### [YYYY-MM-DD] — <Titre court de l'action>
- **Fichier(s) modifié(s)** : `chemin/vers/fichier.py` (lignes X-Y)
- **Nature** : [Ajout | Modification | Suppression | Refactoring | Fix | Sécurité]
- **Raison** : Explication concise du pourquoi
- **Impact** : Modules ou comportements affectés
- **Commit** : `<SHA>` (si applicable)
```

### 3.3 — Gestion des Tokens & Arrêt Préventif

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

### 3.4 — Interopérabilité entre agents

- Utiliser des **commentaires explicites** dans le code : `# TODO(agent): ...`, `# NOTE: ...`, `# SECURITY: ...`
- Ne jamais laisser de code incomplet sans commentaire signalant l'état : `# WIP: implémentation partielle — voir ROADMAP.md`
- Toujours préciser dans ROADMAP.md quel agent a travaillé sur quelle section

***

## 4. Maintenance des Fichiers d'Audit

### 4.1 — Quand mettre à jour TECH_STACK.md

Mettre à jour TECH_STACK.md **obligatoirement** si l'une des conditions suivantes est remplie :

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

### 4.2 — Quand mettre à jour AUDIT_INSTRUCTIONS.md

Mettre à jour AUDIT_INSTRUCTIONS.md **obligatoirement** si l'une des conditions suivantes est remplie :

| Condition | Action |
|-----------|--------|
| Nouveau fichier dans `backend/app/routers/` | Ajouter dans les fichiers cibles du pilier concerné |
| Nouvelle fonctionnalité critique (SSO, export, import, nouveau rôle) | Ajouter les points d'analyse dans le pilier pertinent |
| Faille documentée résolue | Marquer `[RÉSOLU - commit <SHA>]` puis archiver |
| Changement d'infrastructure (Nginx, Kubernetes, reverse proxy...) | Mettre à jour le pilier 1.4 |
| Nouvel endpoint d'authentification | Mettre à jour le pilier 1.1 |

**Règle d'or** : ne jamais supprimer un point d'analyse sans l'avoir marqué `[RÉSOLU]` avec le SHA du commit de correction.

***

## 5. Instructions de Style & Qualité

- **Précision technique maximale** — zéro généralité, zéro approximation
- **Code propre, commenté et modulaire** — chaque fonction a une docstring, chaque module a un commentaire d'en-tête
- **Pas de blabla inutile** — se concentrer sur l'exécution et le suivi de l'avancement
- **Tests obligatoires** pour tout nouveau code métier : pytest + pytest-asyncio
- **Linting avant commit** : `ruff check .` et `mypy` ne doivent retourner aucune erreur bloquante
- **Secrets** : ne jamais hardcoder de valeur sensible — toujours passer par `settings` (pydantic-settings)
- **Pas de `print()`** en production — utiliser le logger configuré dans `main.py`

***

## 6. Arborescence des Fichiers de Pilotage

```
BreachRadar/
├── AGENT.md                    ← ce fichier
├── READ_BEFORE_RUN.md          ← maintenance des fichiers d'audit
├── AUDIT_INSTRUCTIONS.md       ← périmètre et livrables de l'audit sécurité
├── TECH_STACK.md               ← spécifications techniques complètes
├── ROADMAP.md                  ← état d'avancement et changelog
├── SECURITY_BEST-PRACTICE.md   ← bonnes pratiques sécurité du projet
├── audits_reports/             ← rapports d'audit archivés (YYYY-MM-DD_<sha>_audit-report.md)
└── IA_CHANGE.md                ← journal de passation inter-agents
```