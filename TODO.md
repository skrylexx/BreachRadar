# TODO — Mission : Audit des Versions & Dépendances

Ce document définit les étapes pour auditer, sécuriser et mettre à jour la stack technologique de BreachRadar.

## 1. Inventaire & Synchronisation
- [ ] **Audit de Réalité** : Comparer `TECH_STACK.md` avec les fichiers de verrouillage (`package-lock.json`, `pyproject.toml`) pour corriger les versions déclarées.
- [ ] **Documentation des Outils** : Recenser les versions des outils système (Docker, PostgreSQL, Redis, Python, Node) et les figer dans `TECH_STACK.md`.

## 2. Analyse de Sécurité (Backend)
- [ ] **SCA Python** : Lancer un scan de vulnérabilités sur les dépendances Python (ex: `safety` ou `pip-audit`).
- [ ] **Analyse de Drift** : Identifier les packages critiques ayant plus de 2 versions majeures de retard.
- [ ] **Vérification des Images** : Vérifier les vulnérabilités connues des images de base Docker (`python:3.12-slim`).

## 3. Analyse de Sécurité (Frontend)
- [ ] **SCA Node.js** : Exécuter `npm audit` et analyser les rapports de vulnérabilités.
- [ ] **Framework Next.js** : Vérifier si la version actuelle (15.1.3) nécessite des patchs de sécurité critiques.
- [ ] **Audit des Librairies UI** : Vérifier la sécurité des dépendances Tailwind, Lucide-react et Shadcn.

## 4. Livrables & Procédures
- [ ] **PROCEDURE_CHECKS.md** : Finaliser le guide de check réutilisable pour les futures itérations.
- [ ] **Rapport de Drift** : Documenter les recommandations de mise à jour (Priorité Haute / Moyenne / Basse).
- [ ] **Mise à jour TECH_STACK.md** : S'assurer que le fichier est la source de vérité post-audit.

## 5. Remédiation (Optionnel pour cette phase)
- [ ] **Surgical Updates** : Appliquer les mises à jour de sécurité critiques n'introduisant pas de breaking changes.
