# Robotin Development Guide

This guide describes how to work on Robotin during the early development phase.

## Development principles

- Work in small tasks.
- Keep changes narrow.
- Keep the project runnable on Windows.
- Use mocks before real hardware.
- Avoid unnecessary dependencies.
- Keep domain and application code independent from infrastructure.
- Test each useful piece of behavior.

## Recommended workflow

1. Read `MASTER_PROMPT.md`.
2. Read `AGENTS.md`.
3. Check `TASKS.md`.
4. Ask `@architect` for the next smallest task.
5. Ask the correct agent to implement it.
6. Ask `@tester` to add or verify tests.
7. Ask `@safety` to review.
8. Commit the change.

## VS Code workflow

Open the project folder:

```powershell
cd Robotin
code .
```

Use the integrated terminal for:

- Python commands,
- tests,
- opencode,
- Git commits.

## Python environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project after `pyproject.toml` exists:

```powershell
pip install -e .
```

Install development dependencies if defined:

```powershell
pip install -e ".[dev]"
```

## Running Robotin

Once Task 001 exists, run:

```powershell
python -m robotin.main
```

## Running tests

Once tests exist, run:

```powershell
pytest
```

## Working with opencode

Use prompts that specify the agent role.

Example:

```text
Act as @scaffolder.

Implement Task 001 only.
Follow MASTER_PROMPT.md, AGENTS.md, TASKS.md, DECISIONS.md, and SAFETY.md.
Create only the files required for this task.
```

## Git workflow

Use small commits.

Example:

```powershell
git status
git add .
git commit -m "Add Robotin project foundation"
```

## Dependency rules

Before adding a dependency, ask:

1. Can the standard library do this?
2. Is this dependency lightweight?
3. Is it compatible with Raspberry Pi?
4. Is it actively maintained?
5. Can it be isolated in infrastructure?

## Hardware development rule

Do not start with hardware.

Use this progression:

```text
interface
  ↓
mock
  ↓
test
  ↓
simulator if needed
  ↓
real adapter
  ↓
manual hardware test
```

## Linting and formatting

Run before committing:

```powershell
ruff check src tests
ruff format src tests
```

## Review checklist

Before finishing a task, check:

- Does it run on Windows?
- Are tests deterministic?
- Are dependencies minimal?
- Is hardware isolated?
- Are errors clear?
- Is the change small?
- Is documentation updated if needed?
