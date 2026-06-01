# Security Audit Procedures (CI/CD)

## Software Composition Analysis (SCA)

### Python (Backend)
We use `pip-audit` to check for vulnerabilities in our dependencies.
- **Tool**: `uvx pip-audit`
- **Workflow**: 
  1. Export `uv.lock` to `requirements.txt`.
  2. Run `pip-audit` against the requirements file.
- **Failure Handling**: If vulnerabilities are found, check if a patch is available and update `pyproject.toml`.

### JavaScript (Frontend)
We use `npm audit`.
- **Tool**: `npm audit`
- **Workflow**: `cd frontend && npm audit --audit-level=high`
- **Failure Handling**: Run `npm audit fix` locally or manually update `package.json`.

## Secret Detection

We use `detect-secrets` via a GitHub Action.
- **Tool**: `reviewdog/action-detect-secrets`
- **Action**: Monitors all changes in Pull Requests.
- **Best Practice**:
  - Always use `.env.example` as a template.
  - Never commit `.env`.
  - Use `detect-secrets scan` locally before pushing if adding new services.
