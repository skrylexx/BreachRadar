# Contribution Guide — BreachRadar

Thank you for your interest in **BreachRadar**! As an Open Source project, we welcome all contributions: bug reports, new features, documentation corrections, or adding new OSINT connectors.

To guarantee the stability, security, and readability of the project, we ask you to respect the following conventions.

---

## 1. Branch Naming Conventions

We use a strict convention for branch naming to immediately understand the purpose of a *Pull Request* (PR).

Format: `type/short-description-in-english`

| Type | Use Case | Example |
|---|---|---|
| `feat/` | New feature (Frontend or Backend) | `feat/add-alienvault-connector` |
| `fix/` | Bug fix | `fix/scheduler-race-condition` |
| `docs/` | Documentation update (README, guides) | `docs/update-quickstart-docker` |
| `chore/` | Maintenance tasks (CI/CD, dependencies, config) | `chore/update-nextjs-15` |
| `refactor/` | Code refactoring without functional impact | `refactor/api-auth-dependencies` |
| `sec/` | Vulnerability fix / Audit | `sec/harden-jwt-cookies` |

*Example of branch creation:*
```bash
git checkout -b feat/add-slack-notifier
```

---

## 2. Commit Message Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) convention.
A good commit tells a story: it explains **why** this change is made.

**Expected format:**
```text
type(scope): short description in English

- Detailed explanation if necessary.
- Mention any potential impacts.
- Fixes #ISSUE_ID
```

**Examples:**
- ✅ `feat(backend): implement OTX AlienVault integration`
- ✅ `fix(ui): resolve overflow issue on data-table`
- ✅ `docs: add contributing guide`
- ❌ `update files`
- ❌ `fix bug`

---

## 3. Workflow

1. **Fork** the repository and clone it locally.
2. Create a branch (`feat/your-feature`).
3. Write your code respecting the architecture (see `ARCHITECTURE.md` and `AI_AGENT_GUIDE.md`).
4. **Test your code** locally. Do not break existing tests.
   - Backend: `uv run pytest tests/` and `uv run ruff check .`
   - Frontend: `npm run lint` and `npm run build`
5. **Push** your branch to your fork.
6. Open a **Pull Request (PR)** to the `main` branch of the official repository.

---

## 4. Golden Rules and Security (Vital)

BreachRadar is a Cyber tool. **Security is non-negotiable.**

- **NEVER commit secrets** (API keys, passwords, tokens). Always use environment variables (`.env`).
- **Strict Sanitization**: If you add an OSINT connector, all raw data MUST pass through the backend `DataSanitizer` before being sent to the frontend or stored in the database.
- **AI Transparency**: The project contains a `.gemini/` folder. If you use generative AI (Claude, Copilot, Gemini) to help you code, ensure it reads the directives present in this folder to respect our standards.

---

## 5. Review and Validation

As soon as your PR is created:
1. A series of automated tests (GitHub Actions) will run (Mypy, Ruff, NPM/PIP Audit, Bandit). **Your PR must be green.**
2. A `CODEOWNER` (@skrylexx or a designated maintainer) will perform a human review of your code.
3. Adjustments may be requested. Please be responsive!

Thank you for helping us make the world of cybersecurity more accessible and safer! 🚀
