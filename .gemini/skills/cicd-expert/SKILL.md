---
name: cicd-expert
description: Specialized expertise in CI/CD pipelines, GitHub Actions, security audits (SCA, secrets), and automated quality checks. Use when modifying or troubleshooting .github/workflows, adding new CI checks, or ensuring repository integrity through automation.
---

# CI/CD Expert

## Overview

This skill enables Gemini CLI to act as a senior DevOps engineer specialized in CI/CD for the BreachRadar project. It focuses on maintaining a robust, secure, and efficient pipeline using GitHub Actions, `uv` for Python, and standard NPM tools for Frontend.

## Core Responsibilities

1. **Pipeline Maintenance**: Manage `.github/workflows/ci.yml`. Ensure all jobs (security, backend, frontend, docker) are running correctly.
2. **Security Hardening**: Implement and maintain security scans:
   - `detect-secrets`: Secret leak prevention.
   - `npm audit`: Frontend dependency vulnerability scanning.
   - `pip-audit`: Backend dependency vulnerability scanning (via `uv export`).
3. **Quality Assurance**: 
   - Backend: Ruff (linting/formatting), Pytest (unit & security tests).
   - Frontend: ESLint, Next.js build verification.
4. **Infrastructure Validation**: Systematic Docker build checks for both API and UI.

## CI/CD Workflow Patterns

### 1. Adding a New Backend Check
When adding a new check (e.g., `mypy` or `bandit`):
1. Update `backend-checks` job in `ci.yml`.
2. Ensure dependencies are in `pyproject.toml`.
3. Test locally with `rtk uv run <tool>`.

### 2. Dependency Audit Troubleshooting
If `pip-audit` or `npm audit` fails:
1. Identify the vulnerable package.
2. Check `security_audits/TECH_STACK.md` for documented versions.
3. Attempt an update in `pyproject.toml` or `package.json`.
4. Document the fix in `ROADMAP.md` and `AUDIT_INSTRUCTIONS.md`.

### 3. Secret Leak Remediation
If `detect-secrets` fails:
1. Identify the leaked secret.
2. Revoke and rotate the secret if it's real.
3. If it's a false positive, add it to `.secrets.baseline` (if used) or exclude it.
4. NEVER commit real secrets to fix the CI.

## Resources

- `references/github-actions-snippets.md`: Common GitHub Actions snippets for this project.
- `references/security-audit-procedures.md`: Detailed procedures for SCA and secret detection.
