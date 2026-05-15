---
name: tailwind-ui-system
description: Use this skill for Tailwind CSS user interfaces in web apps, especially for dashboards, admin pages, settings pages, forms, tables, cards, responsive layouts, dark mode, accessibility, and clean component styling without unnecessary redesigns.
---

# Tailwind UI System

Use this skill when building or editing UI with Tailwind CSS.

## Goals

- Produce clean, consistent, production-ready UI.
- Match the existing visual language of the repository.
- Prefer readability, spacing consistency, and accessible interactions.
- Avoid flashy redesigns unless explicitly requested.

## Rules

- Reuse existing Tailwind utility patterns already present in the repo.
- Prefer composition over introducing a large custom CSS layer.
- Keep class lists readable and grouped logically: layout, spacing, typography, color, state.
- Do not create visual inconsistency across neighboring pages.
- Favor responsive mobile-first layouts.
- Respect dark mode if the repository already supports it.
- Use semantic HTML first, Tailwind second.

## UI conventions

- Use stable spacing scales; avoid arbitrary values unless already used by the project.
- Keep headings, labels, body text, and helper text visually consistent.
- Prefer neutral surfaces with a restrained accent color.
- Forms: clear labels, visible focus states, actionable validation text.
- Tables: readable density, clear headers, safe overflow handling.
- Cards: subtle separation, not heavy decoration.
- Buttons: consistent heights, padding, and states.
- Empty states and loading states should look intentional.

## Accessibility

- Preserve keyboard navigation.
- Keep focus-visible states clear.
- Ensure sufficient contrast.
- Use proper labels for inputs and buttons.
- Avoid relying on color alone to convey state.

## Editing style

- Do not rewrite all classes on a page just to “clean it up”.
- Touch only the components involved in the request.
- When a reusable pattern repeats 3+ times, propose a component extraction; otherwise keep it local.
- Prefer minimal DOM churn.

## Output style

When implementing UI:
1. Keep structure simple.
2. Reuse existing classes and components.
3. Make the page responsive.
4. Avoid unnecessary visual changes outside scope.