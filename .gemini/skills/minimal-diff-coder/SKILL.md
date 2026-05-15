---
name: minimal-diff-coder
description: Use this skill whenever the task involves editing an existing codebase and the goal is to minimize token usage, reduce code churn, avoid unnecessary refactors, keep patches reviewable, and change only what is strictly required.
---

# Minimal Diff Coder

Use this skill for almost any change in an existing repository.

## Primary objective

Produce the smallest correct patch.

## Hard rules

- Do not rewrite files that do not need changes.
- Do not reformat entire files unless explicitly asked.
- Do not rename, move, or split files without a clear need.
- Do not introduce new abstractions unless duplication is significant and local extraction is clearly beneficial.
- Do not add dependencies unless the task cannot be solved otherwise.
- Do not “improve” unrelated code while touching a file.
- Preserve comments, naming, and conventions unless they block the requested work.
- Prefer editing existing functions/components over replacing them wholesale.

## Token-saving behavior

- Read only the files that are directly relevant.
- Summarize findings tersely.
- Ask for missing files only when blocked.
- Prefer short plans and compact explanations.
- Output concise diffs or focused code edits rather than long essays.

## Safe workflow

1. Identify the exact files involved.
2. Understand the local pattern.
3. Apply the smallest viable change.
4. Verify no unrelated behavior was altered.

## When not to stay minimal

Break the minimal-diff rule only if:
- the existing code is clearly broken for the requested change,
- the local pattern is dangerously inconsistent,
- or a tiny extraction prevents repeated bugs in the exact area being modified.

If you must expand scope, explain why in 1 to 3 sentences max.