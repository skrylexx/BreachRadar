---
name: frontend-page-builder
description: Use this skill for building or finishing frontend pages in an existing product repository, especially dashboard pages, settings screens, admin sections, detail views, empty states, forms, and responsive layouts in Next.js with Tailwind CSS.
---

# Frontend Page Builder

Use this skill when the request is about creating or polishing pages.

## Goals

- Build complete, shippable pages fast.
- Prioritize structure, clarity, and data flow.
- Keep implementation aligned with the repository’s existing components and routes.

## Page-building workflow

1. Identify the route and nearest neighboring pages.
2. Reuse existing layout, spacing, and components.
3. Build the page skeleton first: header, actions, content sections.
4. Add loading, empty, and error states.
5. Connect real or existing mock data paths.
6. Polish responsive behavior.
7. Stop when the page is complete enough for review.

## Page structure guidance

Typical dashboard/admin page:
- Page title and short subtitle
- Primary actions
- Filters/search if relevant
- KPI or summary area if relevant
- Main content region: cards, table, list, or form
- Empty/loading/error states
- Mobile-safe stacking

## Rules

- Do not over-engineer page composition.
- Prefer clear sections over fancy layouts.
- Reuse existing components before creating new ones.
- If data is not available yet, use safe typed placeholders clearly marked for replacement.
- Keep user-facing copy concise and product-specific.

## Responsive behavior

- Mobile-first layout.
- Stack sections vertically on small screens.
- Prevent horizontal overflow.
- Ensure tables and code-like values degrade gracefully on narrow widths.

## Output style

When asked to build a page:
1. Mention route/files.
2. Implement the visible structure first.
3. Add states and responsiveness.
4. Keep the patch narrow.