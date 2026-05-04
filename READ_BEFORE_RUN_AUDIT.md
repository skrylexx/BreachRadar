# READ_BEFORE_RUN — Instructions de Maintenance des Fichiers d'Audit

> Ce fichier est lu **en premier**, avant toute exécution d'audit.
> Il définit comment maintenir la cohérence entre `AUDIT_INSTRUCTIONS.md` et `TECH_STACK.md`
> au fil des évolutions du dépôt BreachRadar.

***

## 0. Ordre d'Exécution Obligatoire

> ℹ️ Cet ordre est spécifique aux sessions d'**audit sécurité**.
> Pour l'ordre de lecture global (développement, refactoring, etc.), se référer à `AGENT.md` section 0.

```
1. READ_BEFORE_RUN.md     ← tu es ici (vérification et mise à jour avant audit)
2. AUDIT_INSTRUCTIONS.md  ← périmètre, livrables, règles d'audit
3. TECH_STACK.md          ← spécifications techniques complètes
```

Ne commencer l'audit qu'après avoir lu les trois fichiers dans cet ordre.

***

## 1. Vérification Préalable au Run

Avant de lancer l'audit, effectuer les vérifications suivantes :

### 1.1 — Comparer le commit actuel avec le dernier commit audité

Récupérer le SHA du dernier commit audité dans `TECH_STACK.md` (champ `Dernier commit audité`).
Comparer avec le HEAD actuel du dépôt via :

```bash
git log --oneline -20
git diff <sha_dernier_audit> HEAD --name-only
```

Si des fichiers ont changé depuis le dernier audit, passer à l'étape 1.2.
Si aucun changement, l'audit peut démarrer directement.

### 1.2 — Identifier les fichiers modifiés depuis le dernier audit

Classifier chaque fichier modifié selon son impact :

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

***

## 2. Mise à Jour de TECH_STACK.md

Mettre à jour `TECH_STACK.md` si l'un des cas suivants est détecté :

### 2.1 — Nouvelles dépendances

Si `pyproject.toml` ou `package.json` contient de nouvelles librairies ou des changements de version :

- Ajouter la librairie dans la section correspondante (Backend section 2 ou Frontend section 3)
- Préciser la version exacte
- Signaler tout package à risque connu (crypto, parsing, HTTP client)

### 2.2 — Nouveaux services Docker

Si `docker-compose.yml` contient un nouveau service :

- Ajouter le service dans la section 4 de `TECH_STACK.md`
- Documenter : image de base, réseaux, volumes, ports, variables d'env injectées

### 2.3 — Nouveaux secrets ou variables d'environnement

Si `.env.example` contient de nouvelles variables :

- Ajouter dans la section 5 de `TECH_STACK.md`
- Classifier : secret sensible (clé API, mot de passe) ou configuration (URL, flag)
- Indiquer si la variable est requise (`:?error`) ou optionnelle (valeur par défaut)

### 2.4 — Nouvelles sources OSINT

Si `backend/app/core/sources.yaml` ou `backend/app/clients/` intègre une nouvelle source :

- Ajouter dans la section 6 de `TECH_STACK.md`
- Documenter : nom de la source, type d'accès (API key, scraping, Tor), données retournées

### 2.5 — Mise à jour du commit de référence

Après chaque mise à jour de `TECH_STACK.md`, mettre à jour le champ :

```
Dernier commit audité : <nouveau SHA>
Date de mise à jour   : <YYYY-MM-DD>
```

***

## 3. Mise à Jour de AUDIT_INSTRUCTIONS.md

Mettre à jour `AUDIT_INSTRUCTIONS.md` si l'un des cas suivants est détecté :

### 3.1 — Nouveaux endpoints ou routers

Si un nouveau fichier apparaît dans `backend/app/routers/` :

- Ajouter le fichier dans la liste **Fichiers cibles** du pilier concerné (section 1.2 ou 1.6)
- Identifier les points de contrôle spécifiques à ce nouveau router (RBAC, validation des entrées, etc.)
- Si le router introduit une nouvelle surface d'attaque non couverte par les six piliers existants, créer un **nouveau pilier** (section 1.7+)

### 3.2 — Nouvelle fonctionnalité critique

Si une nouvelle fonctionnalité est détectée (ex : export, import, SSO, webhook entrant, nouveau rôle utilisateur) :

- Ajouter les points d'analyse correspondants dans le pilier le plus pertinent
- Si la fonctionnalité touche plusieurs piliers, créer des références croisées explicites

### 3.3 — Résolution d'une faille connue

Si une faille documentée dans un rapport d'audit précédent a été corrigée (ex : `/auth/mfa/verify` implémenté) :

- Supprimer ou archiver le point d'analyse correspondant dans `AUDIT_INSTRUCTIONS.md`
- Ajouter une note `[RÉSOLU - commit <SHA>]` dans le point concerné avant suppression définitive
- Ne pas supprimer si la correction est partielle ou non vérifiée

### 3.4 — Changement d'infrastructure

Si l'orchestration évolue (passage de Docker Compose à Kubernetes, ajout d'un reverse proxy Nginx/Traefik, etc.) :

- Mettre à jour le pilier 1.4 (Conteneurisation) avec les nouveaux fichiers cibles
- Ajouter les points d'analyse spécifiques à la nouvelle infrastructure (ex : Ingress rules, NetworkPolicies, RBAC Kubernetes)

***

## 4. Archivage des Rapports d'Audit

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

***

## 5. Contrôle de Cohérence Finale

Avant de clore la session d'audit, vérifier les points suivants :

- [ ] `TECH_STACK.md` reflète l'état actuel du dépôt (pas de dépendance manquante, pas de service non documenté)
- [ ] `AUDIT_INSTRUCTIONS.md` couvre tous les fichiers et composants actifs du dépôt
- [ ] Le champ `Dernier commit audité` dans `TECH_STACK.md` est à jour
- [ ] Le rapport d'audit est archivé dans `audit_reports/` avec la convention de nommage
- [ ] Les failles résolues depuis le dernier audit ont été retirées ou marquées `[RÉSOLU]` dans `AUDIT_INSTRUCTIONS.md`
- [ ] Aucune information sensible (clé API, mot de passe, token) n'apparaît en clair dans les fichiers de documentation