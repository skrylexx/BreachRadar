---
name: docs-readme-writer
description: Use this skill when the task is to create, rewrite, improve, structure, or update project documentation such as README files, setup guides, runbooks, operating procedures, installation steps, contributor guides, technical documentation, architecture notes, deployment guides, onboarding docs, and troubleshooting documentation in Markdown.
---

# Docs README Writer

Use this skill whenever the request is about writing or improving documentation.

This includes:
- README files
- installation guides
- setup procedures
- runbooks
- deployment guides
- onboarding guides
- troubleshooting docs
- architecture overviews
- feature documentation
- admin or operator procedures
- contributor guides
- internal technical notes

## Mission

Write documentation that is:
- accurate,
- easy to scan,
- useful to developers and operators,
- grounded in the actual repository and commands,
- concise but complete enough to execute without guesswork.

## Core principles

- Prefer clarity over completeness theater.
- Prefer concrete commands over vague explanations.
- Prefer structure over long paragraphs.
- Prefer repository truth over assumptions.
- Prefer short sections that answer real user questions.

## Documentation behavior

Before writing:
1. Identify the audience.
2. Identify the goal of the document.
3. Inspect the repository, scripts, config, and relevant files when available.
4. Base documentation on what actually exists.
5. If key information is missing, say what is assumed.

Never invent commands, file paths, environment variables, endpoints, ports, workflows, or deployment steps if they are not supported by the repository or explicitly provided by the user.

## Audience detection

Adapt the document to the likely reader:

- End user: explain usage simply, minimize internal detail.
- Developer: include local setup, commands, file locations, workflows.
- Admin or operator: include procedures, checks, failure cases, rollback notes.
- Contributor: include conventions, branching, testing, pull request workflow.

If the audience is mixed, write for the primary operator first and keep the rest in separate sections.

## README guidance

When writing a `README.md`, prefer this structure when relevant:

1. Project name
2. Short description
3. Key features
4. Stack or architecture summary
5. Prerequisites
6. Installation
7. Configuration
8. Running locally
9. Usage
10. Project structure
11. Common commands
12. Troubleshooting
13. Contributing
14. Security or responsible disclosure
15. License

Do not force every section. Omit sections that are not useful.

A good README should quickly answer:
- What is this project?
- Why does it exist?
- How do I run it?
- What do I need to configure?
- What are the main commands?
- Where should I look next?

## Procedure and runbook guidance

When writing a procedure, use an operational structure:

- Purpose
- Scope
- Preconditions
- Required access or tools
- Step-by-step procedure
- Validation checks
- Expected result
- Failure cases
- Rollback or recovery
- Notes or references

Procedures must be executable by someone who did not write them.

Use numbered steps when order matters.
Use exact commands when available.
Add warnings before risky actions, not after them.

## Technical documentation guidance

For architecture or technical docs:
- describe the system in layers,
- explain responsibilities and boundaries,
- name the key directories, services, or modules,
- show request/data flow when relevant,
- call out assumptions and integration points,
- highlight operational or security-sensitive areas.

Do not drown the reader in implementation trivia.
Start from the system view, then go narrower.

## Style rules

- Write in Markdown.
- Use short, descriptive headings.
- Keep paragraphs short.
- Use bullets for lists of facts or options.
- Use numbered lists for procedures.
- Use fenced code blocks for commands, config, JSON, YAML, shell, or code.
- Use tables only when comparing structured information.
- Use plain language.
- Avoid marketing tone.
- Avoid filler phrases and generic hype.
- Avoid unexplained jargon unless the audience is clearly expert.
- Keep commands copy-paste ready.

## Command and code block rules

- Commands must be realistic and runnable.
- Do not include placeholder values unless clearly marked.
- If placeholders are necessary, make them obvious, for example:
  - `<YOUR_API_KEY>`
  - `<DOMAIN>`
  - `<PROJECT_ROOT>`
- Separate shell commands from explanatory text.
- Do not mix multiple shells in one example unless necessary.
- Respect the repository’s actual package manager and tooling.

## Repository-grounded writing

When repository access is available:
- inspect package manifests,
- inspect Docker files and compose files,
- inspect env examples,
- inspect scripts and Makefiles,
- inspect CI workflows,
- inspect source directories,
- inspect existing docs before rewriting them.

If an existing document already exists, improve it instead of replacing it blindly unless the user asks for a rewrite.

## README quality checklist

A README should:
- identify the project clearly,
- explain the purpose in 2 to 5 lines,
- provide setup and run commands,
- mention configuration needs,
- describe the main modules or folders when useful,
- include troubleshooting if setup is non-trivial,
- avoid stale or speculative sections,
- match the current codebase.

## Procedure quality checklist

A procedure should:
- define the purpose,
- list prerequisites,
- use ordered steps,
- include validation checks,
- mention failure or rollback handling,
- be executable without hidden context.

## Documentation update policy

When updating existing documentation:
- preserve useful content,
- remove stale instructions,
- normalize wording,
- fix inaccurate commands,
- avoid changing unrelated sections,
- keep diffs reviewable.

## Security and operational documentation

When documenting security-sensitive workflows:
- never expose real secrets,
- use placeholder values,
- mention least-privilege expectations when relevant,
- document risky commands carefully,
- include validation and rollback where applicable.

## Preferred output formats

Generate documentation in:
- `README.md`
- `docs/*.md`
- `RUNBOOK.md`
- `DEPLOYMENT.md`
- `CONTRIBUTING.md`
- `TROUBLESHOOTING.md`
- `ARCHITECTURE.md`

Choose the smallest appropriate document for the request.

## Good triggers for this skill

Activate this skill for requests such as:
- write me a README
- improve this README
- document the setup
- write the deployment procedure
- create onboarding docs
- document this feature
- write a runbook
- explain the procedure step by step
- write technical documentation for this repo
- create a troubleshooting guide

## Coordination with other local skills

When relevant, align with:
- minimal-diff-coder, to keep doc edits scoped
- repo-context-breachradar, to preserve product terminology
- senior-webapp-cyber-auditor, for security and hardening sections
- nextjs-app-router, tailwind-ui-system, and python-api-backend, for stack-specific accuracy

## Output expectations

When asked to write docs:
1. Determine the document type.
2. Infer the audience.
3. Gather repo facts.
4. Produce a clear structure.
5. Write concise, accurate Markdown.
6. Include commands and paths only when verified or explicitly provided.
7. Mention assumptions briefly when verification is incomplete.