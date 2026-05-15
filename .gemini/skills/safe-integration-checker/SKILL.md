---
name: safe-integration-checker
description: Use this skill when a change may affect integration between frontend and backend, environment variables, Docker setup, API routes, request payloads, response shapes, or branch-safe feature delivery in an existing full-stack repository.
---

# Safe Integration Checker

Use this skill before or during changes that may break integration.

## Purpose

Catch integration risks early while keeping changes small.

## Checklist

- Does the frontend call an existing endpoint contract correctly?
- Are request payload names aligned with backend expectations?
- Are response fields handled defensively?
- Are env vars read from the correct runtime side?
- Are Docker or compose assumptions impacted?
- Are auth, CORS, ports, or base URLs affected?
- Is a fallback state shown if the backend is unavailable?
- Is the branch change isolated enough for review and merge?

## Rules

- Prefer compatibility over elegance.
- If an API contract change is needed, note both sides explicitly.
- Do not silently change field names across layers.
- Flag missing env vars and migration risks.
- Keep verification steps practical and short.

## Verification style

For any integration-sensitive task, provide a compact check list:
- files touched
- contract changes
- env impact
- runtime impact
- quick manual verification path

## Output style

Use short, operational language.
Do not produce long explanations unless risk is high.