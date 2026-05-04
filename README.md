# Robotin

Robotin is a small child-friendly robot project designed to run first as a mock-based Python application on Windows and later on Raspberry Pi OS Lite 64-bit.

The project is intentionally built in small, safe, testable phases.

## Goals

Robotin should eventually support:

- expressive eyes/display,
- microphone input,
- wake word detection,
- local STT,
- local TTS,
- local AI interaction,
- robot state handling,
- offline-first operation,
- Raspberry Pi deployment.

## Initial development approach

The initial version does **not** use real hardware.

The first goal is to build the base robot brain with:

- a simple state machine,
- mock display,
- mock AI client,
- mock TTS,
- console-based text input,
- tests,
- clean architecture.

## Architecture principles

Robotin follows a modular architecture:

```text
domain/         Pure robot logic
application/    Use case orchestration
interfaces/     Contracts for external capabilities
infrastructure/ Concrete mocks and adapters
```

The core rule is:

```text
Domain and application code must not know whether Robotin is running on Windows, Raspberry Pi 4, or Raspberry Pi 5.
Only infrastructure adapters may know that.
```

## Planned structure

```text
Robotin/
├── AGENTS.md
├── MASTER_PROMPT.md
├── TASKS.md
├── DECISIONS.md
├── SAFETY.md
├── pyproject.toml
├── README.md
├── .env.example
├── assets/
│   ├── sounds/
│   └── eyes/
├── docs/
│   ├── architecture.md
│   ├── development.md
│   ├── raspberry_setup.md
│   └── protocol.md
├── src/
│   └── robotin/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── state_machine.py
│       ├── events.py
│       ├── interfaces/
│       ├── infrastructure/
│       ├── application/
│       └── domain/
└── tests/
```

## Development environment

Initial development target:

- Windows
- VS Code
- Python
- opencode

Later deployment target:

- Raspberry Pi OS Lite 64-bit
- Raspberry Pi 4 initially
- Raspberry Pi 5 later

## Working with opencode

Use `AGENTS.md` to guide opencode behavior.

Recommended workflow:

1. Ask `@architect` for the smallest next task.
2. Ask the implementation agent to implement only that task.
3. Ask `@tester` to add or verify tests.
4. Ask `@safety` to review.
5. Commit the small change.

Example prompt:

```text
Act as @architect.

Read MASTER_PROMPT.md, AGENTS.md, TASKS.md, DECISIONS.md, and SAFETY.md.
Inspect the current project.
Propose the smallest useful next task.
Do not write code yet.
```

## First task

The first task is defined in `TASKS.md` as:

```text
Task 001 - Project foundation
```

It creates:

- the initial Python project structure,
- a minimal state machine,
- a mock display,
- an executable `main.py`,
- a minimal test.

## Safety

Robotin may later control physical hardware.

For that reason:

- no real hardware control should be added early,
- all hardware logic must be isolated in infrastructure adapters,
- mocks must remain available,
- external calls must have timeouts,
- physical hardware execution must be reviewed manually.
