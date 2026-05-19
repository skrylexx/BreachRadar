# BreachRadar — GEMINI.md

## Rôle
Tu assistes au développement de BreachRadar, une plateforme de veille cyber / OSINT / détection de fuites de données / ransomware.

## Priorités
1. Lire et respecter les fichiers de pilotage présents dans le dépôt.
2. Préserver la cohérence de l’architecture existante.
3. Produire des modifications minimales, sûres et documentées.
4. Ne pas casser les workflows Docker, FastAPI, Next.js, Python, Node.js, et les scripts existants.
5. Favoriser la lisibilité, la maintenabilité et la sécurité.

## Contexte projet
- Backend Python / FastAPI.
- Frontend Next.js.
- Usage de Docker / Docker Compose.
- Projet orienté cybersécurité, monitoring, et intégration d’APIs externes.
- Toujours vérifier les fichiers de référence du projet avant d’agir.

## Instructions de travail
- Commence par identifier les fichiers pertinents avant de modifier quoi que ce soit.
- Si une tâche concerne le dépôt, privilégie les fichiers de documentation et de pilotage avant les changements de code.
- Ne réécris pas l’architecture sans nécessité.
- N’introduis pas de dépendances supplémentaires sans justification claire.
- Quand une commande shell est nécessaire, privilégie les formes simples et lisibles.

## RTK
- Utilise RTK pour réduire la verbosité des commandes shell quand c’est possible.
- Préfixe les commandes longues ou bavardes avec `rtk` si le contexte le permet.
- Pour les commandes de diagnostic, `git`, `docker`, `test`, `ls`, `dir`, `grep`, `find`, `pytest`, `npm`, et similaires, essaie d’utiliser RTK pour limiter la sortie inutile.
- Si RTK est disponible, préfère son usage pour les commandes génératrices de beaucoup de sortie.

## Sécurité shell
- Évite les commandes avec substitution si une alternative simple existe.
- Préfère des commandes explicites en plusieurs étapes plutôt qu’une seule commande imbriquée.
- Évite autant que possible :
  - `$(...)`
  - backticks
  - chaînes de commandes complexes dans un seul appel
- Si une substitution semble nécessaire, cherche d’abord une version équivalente plus simple et plus sûre.
- N’exécute pas de commandes shell ambiguës si une variante claire existe.

## Style de réponse
- Réponses concises, techniques, actionnables.
- Pas de remplissage inutile.
- Si tu proposes du code, il doit être directement exploitable.
- Si tu modifies des fichiers, explique brièvement ce qui change et pourquoi.

## Règles projet
- Respecter les conventions déjà présentes dans le dépôt.
- Vérifier les fichiers d’audit et de traçabilité si la tâche touche à l’architecture, la sécurité ou à la documentation centrale.
- Ne pas inventer de structure si le dépôt en impose déjà une.

## Préférence générale
- Favoriser les solutions simples.
- Favoriser la robustesse.
- Favoriser les commandes qui évitent les substitutions de shell.
- Favoriser RTK pour économiser des tokens et réduire la sortie des commandes lorsque c’est utile.