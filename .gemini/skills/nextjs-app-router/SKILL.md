---
name: nextjs-app-router
description: Use this skill for Next.js App Router development in TypeScript or JavaScript, including app directory architecture, layouts, pages, route handlers, server components, client components, loading states, error boundaries, metadata, environment variables, and safe frontend changes in existing repositories.
---

# Next.js App Router

Use this skill when working on a Next.js application that uses the App Router.

## Goals

- Prefer small, local changes over broad rewrites.
- Preserve the existing project structure and conventions.
- Use App Router idioms, not Pages Router patterns.
- Keep code maintainable, typed where possible, and easy to review.

## Rules

- Assume the project uses the `app/` directory unless files prove otherwise.
- Prefer Server Components by default.
- Add `"use client"` only when interactivity, browser APIs, hooks, or client state are required.
- Do not convert Server Components to Client Components unless strictly necessary.
- Keep `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, and route handlers focused and minimal.
- When editing existing files, preserve exports, naming, and folder conventions.
- Do not introduce new dependencies unless the task requires them.
- Reuse existing utilities, UI primitives, hooks, and lib functions before creating new ones.
- Keep metadata and SEO declarations localized and simple.
- Use route handlers in `app/api/.../route.ts` when backend work belongs inside the Next app.
- If the repository already has a separate Python backend, avoid duplicating backend logic in Next.js.

## Component guidance

- Server Components for data-driven rendering and static structure.
- Client Components only for forms, event handlers, browser APIs, controlled inputs, interactive widgets, or local UI state.
- Pass serializable props from server to client components.
- Avoid deeply nested client trees when a single interactive leaf is enough.

## Data and env guidance

- Read secrets only on the server side.
- Never expose sensitive backend keys in client code.
- Prefer existing env variable names and patterns already used by the repo.
- If adding a fetch call, keep error handling explicit and user-safe.

## File editing style

- Modify only the files needed for the request.
- Keep diffs reviewable.
- Do not rename files or move folders unless asked.
- Do not restyle unrelated pages while implementing one page.

## Output style

When asked to implement something:
1. Identify the smallest viable files to change.
2. Describe the plan briefly.
3. Apply the change with minimal collateral edits.
4. Mention any assumptions or follow-up checks.