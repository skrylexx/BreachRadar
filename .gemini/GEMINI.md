# BreachRadar — GEMINI.md

## Role
You assist in the development of BreachRadar, a cyber intelligence / OSINT / data leak detection / ransomware platform.

## Priorities
1. Read and respect the steering files present in the repository.
2. Preserve the consistency of the existing architecture.
3. Produce minimal, safe, and documented changes.
4. Do not break Docker, FastAPI, Next.js, Python, Node.js workflows, or existing scripts.
5. Favor readability, maintainability, and security.

## Project Context
- Python / FastAPI Backend.
- Next.js Frontend.
- Use of Docker / Docker Compose.
- Project focused on cybersecurity, monitoring, and integration of external APIs.
- Always check the project reference files before acting.

## Working Instructions
- Start by identifying relevant files before modifying anything.
- If a task concerns the repository, prioritize documentation and steering files before code changes.
- Do not rewrite the architecture unnecessarily.
- Do not introduce additional dependencies without clear justification.
- When a shell command is necessary, prioritize simple and readable forms.

## RTK
- Use RTK to reduce the verbosity of shell commands whenever possible.
- Prefix long or verbose commands with `rtk` if the context allows.
- For diagnostic commands, `git`, `docker`, `test`, `ls`, `dir`, `grep`, `find`, `pytest`, `npm`, and similar, try to use RTK to limit unnecessary output.
- If RTK is available, prefer its use for commands that generate a lot of output.

## Shell Security
- Avoid commands with substitution if a simple alternative exists.
- Prefer explicit multi-step commands over a single nested command.
- Avoid as much as possible:
  - `$(...)`
  - backticks
  - complex command chains in a single call
- If substitution seems necessary, first look for a simpler and safer equivalent version.
- Do not execute ambiguous shell commands if a clear variant exists.

## Response Style
- Concise, technical, actionable responses.
- No unnecessary filler.
- If you propose code, it must be directly usable.
- If you modify files, briefly explain what changes and why.

## Project Rules
- Respect conventions already present in the repository.
- Check audit and traceability files if the task touches architecture, security, or central documentation.
- Do not invent structure if the repository already imposes one.

## General Preference
- Favor simple solutions.
- Favor robustness.
- Favor commands that avoid shell substitutions.
- Favor RTK to save tokens and reduce command output when useful.
