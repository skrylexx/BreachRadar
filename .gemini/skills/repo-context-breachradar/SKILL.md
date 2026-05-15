---
name: repo-context-breachradar
description: Use this skill when working on the BreachRadar repository, especially for frontend pages, admin settings, connectors, dashboard views, domain monitoring flows, breach and ransomware data presentation, and safe coordination between the Next.js frontend and the Python backend.
---

# BreachRadar Repository Context

This skill is specific to the BreachRadar project.

## Project assumptions

- BreachRadar is a cybersecurity monitoring application.
- The repo likely contains a Next.js frontend and a Python backend.
- Key product areas include breaches, ransomware monitoring, domain-focused views, connectors, settings, and dashboard-style pages.
- The active work often targets frontend implementation without breaking backend integration.

## Working principles

- Preserve the product direction: operational, security-focused, clear, and functional.
- Prefer admin/dashboard UX over marketing-style UI.
- Keep terminology consistent with cybersecurity operations.
- Do not invent product capabilities that the codebase does not already support.
- Avoid fake metrics, fake charts, or placeholder security claims in production code.

## Frontend priorities

- Clear hierarchy for dashboards and settings pages.
- Dense but readable layouts.
- Strong empty states, loading states, and error states.
- Tables, cards, filters, and status indicators should feel operational, not decorative.

## Backend coordination

- If the frontend consumes existing endpoints, adapt to the current contract first.
- Do not change API contracts casually when building pages.
- Surface backend failures clearly to the UI without exposing internals.

## Branch mindset

Assume current work may be on feature delivery for frontend pages.
Keep changes isolated and review-friendly.

## Output style

When implementing features in BreachRadar:
1. Align to existing product language.
2. Keep UX operational and credible.
3. Reuse current data contracts.
4. Avoid speculative architecture changes.