# IA_CHANGE.md — Journal de Passation Inter-Agents

> Ce fichier est le point d'entrée opérationnel pour tout agent IA qui reprend le projet.
> Il contient le prompt de reprise standardisé, l'historique des passations, et les règles de handoff.
> À mettre à jour à **chaque fin de session** avant de clore le contexte.

***

## 0. Prompt de Reprise Rapide

Copier-coller ce bloc pour démarrer une nouvelle session sur n'importe quel agent IA :

```
Tu reprends le développement du projet BreachRadar.
Lien repo : https://github.com/skrylexx/BreachRadar

Lis les fichiers suivants dans cet ordre AVANT de faire quoi que ce soit :
1. AGENT.md               — mission, protocoles, règles de traçabilité
2. READ_BEFORE_RUN.md     — maintenance des fichiers d'audit
3. AUDIT_INSTRUCTIONS.md  — périmètre et livrables de l'audit sécurité
4. TECH_STACK.md          — spécifications techniques complètes
5. ROADMAP.md             — état d'avancement exact et prochaine tâche

Respecte scrupuleusement le protocole de traçabilité défini dans AGENT.md (section 3) :
documenter chaque changement dans ROADMAP.md, mettre à jour TECH_STACK.md et
AUDIT_INSTRUCTIONS.md si nécessaire, remplir la section "Prochain Agent" avant
d'atteindre la limite de ta fenêtre de contexte.
```

***

## 1. Règles de Passation

### 1.1 — Ce que l'agent sortant DOIT faire avant de clore sa session

- [ ] Mettre à jour **ROADMAP.md** : CHANGELOG de la session + section `Prochain Agent — Reprendre ici`
- [ ] Mettre à jour **TECH_STACK.md** si la stack a évolué (nouvelles dépendances, services, secrets)
- [ ] Mettre à jour **AUDIT_INSTRUCTIONS.md** si de nouveaux composants ont été ajoutés
- [ ] Ajouter une entrée dans la section **2. Historique des Passations** ci-dessous
- [ ] Pousser un commit avec le message : `docs: mise à jour ROADMAP + IA_CHANGE [fin session <agent>]`

### 1.2 — Ce que l'agent entrant DOIT faire avant de commencer

- [ ] Lire les 5 fichiers de référence dans l'ordre (voir section 0)
- [ ] Vérifier le dernier commit audité dans TECH_STACK.md vs HEAD actuel
- [ ] Consulter la section `Prochain Agent — Reprendre ici` dans ROADMAP.md
- [ ] Ne pas modifier de code avant d'avoir lu ces fichiers

### 1.3 — Format d'une entrée de passation

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

## 2. Historique des Passations

### Passation #1 — 2026-05-04

- **Agent sortant**            : Claude (Perplexity — session initiale de structuration)
- **Agent entrant**            : indéfini
- **Commit de fin de session** : `08508ac`
- **Tâches accomplies** :
  - Architecture complète en place (backend FastAPI + frontend Next.js + Docker Compose)
  - Création et structuration de tous les fichiers de pilotage :
    `AGENT.md`, `READ_BEFORE_RUN.md`, `AUDIT_INSTRUCTIONS.md`, `TECH_STACK.md`, `IA_CHANGE.md`
- **Tâche suivante** : Voir section `Prochain Agent — Reprendre ici` dans ROADMAP.md
- **Points de vigilance** :
  - `/auth/mfa/verify` retourne `501 NOT_IMPLEMENTED` — MFA non fonctionnel en l'état
  - `curl | sh` dans `backend/Dockerfile` — risque supply chain (aucune vérification d'intégrité)
  - Images Docker `dperson/torproxy:latest` et `travishunting/ransomlook:latest` non épinglées
  - CSP avec `unsafe-eval` + `unsafe-inline` dans `frontend/next.config.ts`
  - `UI_REDIS_PASSWORD` visible dans la commande `redis-server` (docker inspect / ps aux)
- **Fichiers mis à jour** : AGENT.md · TECH_STACK.md · AUDIT_INSTRUCTIONS.md · READ_BEFORE_RUN.md · IA_CHANGE.md

***

## 3. Référence Rapide — Fichiers de Pilotage

| Fichier | Rôle | Mettre à jour quand ? |
|---------|------|-----------------------|
| `AGENT.md` | Mission, protocoles, règles globales | Changement de workflow ou de convention |
| `READ_BEFORE_RUN.md` | Maintenance des fichiers d'audit | Ajout d'un nouveau type de fichier critique |
| `AUDIT_INSTRUCTIONS.md` | Périmètre et livrables de l'audit | Nouveau composant, faille résolue, nouveau pilier |
| `TECH_STACK.md` | Spécifications techniques complètes | Toute évolution de la stack ou des dépendances |
| `ROADMAP.md` | Avancement, CHANGELOG, prochaine tâche | **À chaque fin de session, sans exception** |
| `IA_CHANGE.md` | Journal de passation inter-agents | **À chaque fin de session, sans exception** |
| `audits_reports/` | Rapports d'audit archivés | Après chaque audit sécurité |