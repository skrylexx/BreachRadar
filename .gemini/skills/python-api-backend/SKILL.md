---
name: python-api-backend
description: Use this skill for Python backend API work, including FastAPI or Flask style endpoints, request and response models, validation, configuration, environment variables, connectors, background jobs, security-sensitive changes, and integration with a Next.js frontend.
---

# Python API Backend

Use this skill for backend work in Python.

## Goals

- Make safe backend changes with explicit validation and error handling.
- Preserve existing architecture and conventions.
- Keep API contracts stable when possible.
- Avoid leaking secrets or weakening security.

## Rules

- Inspect the current backend structure before adding new modules.
- Reuse existing config, settings, routers, schemas, and helpers.
- Validate inputs explicitly.
- Return predictable response shapes.
- Keep errors actionable but not overly verbose.
- Avoid silent failures.
- Do not hardcode secrets, URLs, tokens, or credentials.
- Prefer environment-based configuration consistent with the repo.
- Preserve backward compatibility unless the request says otherwise.

## API design

- Keep endpoint responsibilities narrow.
- Use clear naming for routes and payload fields.
- Separate transport concerns from service logic where the codebase already follows that pattern.
- If pagination, filtering, or sorting exists elsewhere, mirror the same contract style.

## Security

- Treat all external data as untrusted.
- Sanitize and validate connector inputs.
- Avoid exposing stack traces to frontend consumers.
- Do not relax auth, CORS, or permission checks without explicit instruction.
- Flag risky changes clearly.

## Integration with Next.js

- Keep response payloads easy for frontend consumption.
- Document changed request and response fields briefly.
- Do not duplicate frontend formatting logic in the API unless necessary.

## Editing style

- Change the narrowest possible set of files.
- Reuse existing test or example patterns if present.
- Avoid broad refactors while implementing one endpoint or connector.

## Output style

For backend changes:
1. State the contract impact.
2. Implement the smallest safe change.
3. Note any env vars or migration implications.
4. Mention verification steps briefly.