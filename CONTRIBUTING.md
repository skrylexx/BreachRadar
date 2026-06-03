# Guide de Contribution — BreachRadar

Merci de l'intérêt que vous portez à **BreachRadar** ! En tant que projet Open Source, nous accueillons toutes les contributions : rapports de bugs, nouvelles fonctionnalités, corrections de documentation ou ajout de nouveaux connecteurs OSINT.

Pour garantir la stabilité, la sécurité et la lisibilité du projet, nous vous demandons de respecter les conventions suivantes.

---

## 1. Conventions de Nommage des Branches

Nous utilisons une convention stricte pour le nommage des branches afin de comprendre immédiatement le but d'une *Pull Request* (PR).

Format : `type/courte-description-en-anglais`

| Type | Cas d'usage | Exemple |
|---|---|---|
| `feat/` | Nouvelle fonctionnalité (Frontend ou Backend) | `feat/add-alienvault-connector` |
| `fix/` | Correction de bug | `fix/scheduler-race-condition` |
| `docs/` | Mise à jour de la documentation (README, guides) | `docs/update-quickstart-docker` |
| `chore/` | Tâches de maintenance (CI/CD, dépendances, config) | `chore/update-nextjs-15` |
| `refactor/` | Refactorisation de code sans impact fonctionnel | `refactor/api-auth-dependencies` |
| `sec/` | Correction de vulnérabilité / Audit | `sec/harden-jwt-cookies` |

*Exemple de création de branche :*
```bash
git checkout -b feat/add-slack-notifier
```

---

## 2. Conventions des Messages de Commit

Nous suivons la convention [Conventional Commits](https://www.conventionalcommits.org/).
Un bon commit raconte une histoire : il explique **pourquoi** ce changement est fait.

**Format attendu :**
```text
type(scope): description courte en anglais

- Explication détaillée si nécessaire.
- Mentionne les éventuels impacts.
- Fixes #ID_DE_L_ISSUE
```

**Exemples :**
- ✅ `feat(backend): implement OTX AlienVault integration`
- ✅ `fix(ui): resolve overflow issue on data-table`
- ✅ `docs: add contributing guide`
- ❌ `update files`
- ❌ `fix bug`

---

## 3. Le Flux de Travail (Workflow)

1. **Forkez** le dépôt et clonez-le localement.
2. Créez une branche (`feat/votre-fonctionnalite`).
3. Écrivez votre code en respectant l'architecture (voir `ARCHITECTURE.md` et `AI_AGENT_GUIDE.md`).
4. **Testez votre code** en local. Ne cassez pas les tests existants.
   - Backend : `uv run pytest tests/` et `uv run ruff check .`
   - Frontend : `npm run lint` et `npm run build`
5. **Poussez** (Push) votre branche sur votre fork.
6. Ouvrez une **Pull Request (PR)** vers la branche `main` du dépôt officiel.

---

## 4. Règles d'Or et Sécurité (Vital)

BreachRadar est un outil Cyber. **La sécurité est non négociable.**

- **Ne commitez JAMAIS de secrets** (Clés API, mots de passe, tokens). Utilisez toujours des variables d'environnement (`.env`).
- **Sanitisation stricte** : Si vous ajoutez un connecteur OSINT, toutes les données brutes DOIVENT passer par le `DataSanitizer` du backend avant d'être envoyées au frontend ou stockées en base.
- **Transparence IA** : Le projet contient un dossier `.gemini/`. Si vous utilisez une IA générative (Claude, Copilot, Gemini) pour vous aider à coder, assurez-vous qu'elle lise les directives présentes dans ce dossier pour respecter nos standards.

---

## 5. Review et Validation

Dès la création de votre PR :
1. Une série de tests automatisés (GitHub Actions) va se lancer (Mypy, Ruff, Audit NPM/PIP, Bandit). **Votre PR doit être au vert.**
2. Un `CODEOWNER` (@skrylexx ou un mainteneur désigné) fera une relecture humaine de votre code.
3. Des ajustements pourront vous être demandés. Soyez réactifs !

Merci de nous aider à rendre le monde de la cybersécurité plus accessible et plus sûr ! 🚀