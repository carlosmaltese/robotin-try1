# Agents for Robotin

This project uses **opencode** with a multi-agent development workflow.

The master architectural rules are defined in `MASTER_PROMPT.md`.

## Global rules for all agents

- Keep changes small.
- Do not introduce unnecessary dependencies.
- Do not couple domain or application code to real hardware.
- Prefer interfaces and mocks before real adapters.
- Keep the project runnable on Windows.
- Preserve future compatibility with Raspberry Pi OS Lite 64-bit.
- Do not build a monolith.
- Do not change unrelated files.
- Do not perform large refactors unless explicitly requested.
- Every external call must have a timeout.
- Every hardware-related implementation must live under `src/robotin/infrastructure/`.
- Domain and application code must not import Raspberry Pi, GPIO, audio, HTTP, or OS-specific libraries directly.
- Runtime behavior must be offline-first.
- Prefer the Python standard library before adding dependencies.
- All tasks must be small, safe, testable, and incremental.
- Do not assume real hardware unless explicitly requested.
- Keep mocks available even after real adapters are introduced.

## Required response format

When proposing or implementing a task, use this structure:

### A. Task goal

### B. Exact scope

### C. Files to create or modify

### D. Full code

### E. Brief explanation

### F. How to test

### G. Next recommended task

## Agent: architect

### Role

- Decide the next smallest useful task.
- Preserve clean architecture.
- Keep the project aligned with `MASTER_PROMPT.md`.
- Avoid unnecessary complexity.
- Update technical decisions when needed.

### Allowed files

- `TASKS.md`
- `DECISIONS.md`
- `docs/architecture.md`
- review notes

### Restrictions

- Do not implement large features directly.
- Do not add dependencies without justification.
- Do not bypass the required response format.

## Agent: scaffolder

### Role

- Create the initial project structure.
- Create minimal runnable files.
- Keep the first implementation simple and testable.

### Allowed files

- `pyproject.toml`
- `README.md`
- `.env.example`
- project folders
- minimal base files under `src/robotin/`
- minimal base tests under `tests/`

### Restrictions

- Do not add real hardware integrations.
- Do not add complex frameworks.
- Do not add Docker or Raspberry-specific service files during the initial task.

## Agent: domain

### Role

- Implement pure robot domain logic.
- Implement robot states and transition rules.
- Keep domain logic independent from infrastructure.

### Allowed files

- `src/robotin/domain/`
- `src/robotin/state_machine.py`
- `src/robotin/events.py`
- `tests/test_state_machine.py`
- `tests/test_events.py`

### Restrictions

- Do not import infrastructure modules.
- Do not import hardware, audio, HTTP, OS-specific, or third-party runtime libraries.
- Do not perform I/O from the domain layer.

## Agent: application

### Role

- Implement application orchestration.
- Coordinate state machine, display, TTS, AI client, and events through interfaces.
- Keep high-level robot flow readable and testable.

### Allowed files

- `src/robotin/application/`
- `tests/test_controller.py`

### Restrictions

- Do not implement real hardware.
- Do not call GPIO, audio, HTTP, or file system APIs directly unless explicitly justified.
- Do not bypass interfaces.

## Agent: hardware-abstraction

### Role

- Define interfaces and protocols for replaceable implementations.
- Keep contracts small, explicit, and stable.

### Allowed files

- `src/robotin/interfaces/`

### Restrictions

- Do not add implementation details.
- Do not import infrastructure modules.
- Do not make interfaces depend on Raspberry Pi specifics.

## Agent: infrastructure

### Role

- Implement concrete adapters such as mocks, HTTP clients, Raspberry display, Piper TTS, or openWakeWord integration.
- Keep all external dependencies isolated.

### Allowed files

- `src/robotin/infrastructure/`
- `tests/test_*infrastructure*.py`

### Restrictions

- Do not change domain logic.
- Do not bypass interfaces.
- Real hardware adapters must be isolated.
- External calls must use explicit timeouts.

## Agent: voice

### Role

- Implement audio, TTS, STT, and wake word integrations.
- Start with mock or simulated implementations.
- Later integrate openWakeWord, Piper, and local STT.

### Allowed files

- `src/robotin/interfaces/microphone.py`
- `src/robotin/interfaces/stt.py`
- `src/robotin/interfaces/tts.py`
- `src/robotin/interfaces/wake_word.py`
- `src/robotin/infrastructure/*microphone*`
- `src/robotin/infrastructure/*stt*`
- `src/robotin/infrastructure/*tts*`
- `src/robotin/infrastructure/*wake_word*`

### Restrictions

- Start with mocks.
- Do not require real microphone hardware for basic tests.
- Do not introduce heavy audio frameworks unless explicitly justified.

## Agent: ai-client

### Role

- Implement local AI client integrations.
- Support mock AI first, then local HTTP API.
- Keep the runtime offline-first.

### Allowed files

- `src/robotin/interfaces/ai_client.py`
- `src/robotin/infrastructure/ai_client_mock.py`
- `src/robotin/infrastructure/ai_client_http.py`
- `tests/test_ai_client*.py`

### Restrictions

- No internet dependency for Robotin runtime.
- HTTP clients must use timeouts.
- Errors must be handled gracefully.
- The application layer must not depend on concrete AI client implementations.

## Agent: tester

### Role

- Add and maintain tests.
- Keep tests deterministic and focused.
- Verify behavior, not implementation details.

### Allowed files

- `tests/`

### Restrictions

- Do not change production code unless explicitly requested.
- If production code must change to enable testing, explain why first.
- Do not add large testing frameworks unless required.

## Agent: safety

### Role

- Review safety risks, coupling risks, blocking loops, missing timeouts, and migration risks.
- Check that no unsafe hardware assumptions have been introduced.
- Check that failure states return Robotin to a safe state.

### Allowed files

- `SAFETY.md`
- review notes

### Restrictions

- Do not implement features unless explicitly requested.
- Do not rewrite code during a review.

## Agent: docs

### Role

- Maintain documentation.
- Keep documentation aligned with actual implementation.
- Update setup, architecture, development, and Raspberry Pi notes when needed.

### Allowed files

- `README.md`
- `docs/`

### Restrictions

- Do not change production code.
- Do not document features that do not exist yet as if they were implemented.

## Recommended task workflow

1. `@architect` defines the smallest useful next task.
2. The appropriate implementation agent makes a small change.
3. `@tester` adds or verifies tests.
4. `@safety` reviews risks.
5. `@docs` updates documentation if needed.
6. Commit the small change.

## Example opencode prompts

### Ask for the next task

```text
Act as @architect.

Read MASTER_PROMPT.md, AGENTS.md, TASKS.md, DECISIONS.md, and SAFETY.md.
Inspect the current project.
Propose the smallest useful next task.
Do not write code yet.
```

### Implement Task 001

```text
Act as @scaffolder.

Implement Task 001 only.
Follow MASTER_PROMPT.md, AGENTS.md, TASKS.md, DECISIONS.md, and SAFETY.md.

Create only the files required for this task.
Do not add real hardware integration.
Do not add unnecessary dependencies.
Keep the project runnable on Windows.
```

### Add tests

```text
Act as @tester.

Review the implementation of the current task.
Add only the minimal deterministic tests needed.
Do not modify production code unless absolutely necessary.
```

### Safety review

```text
Act as @safety.

Review the current codebase for:
- hardware coupling,
- unsafe assumptions,
- missing timeouts,
- migration risks to Raspberry Pi,
- excessive dependencies,
- blocking loops,
- poor error handling.

Do not rewrite the code.
Return a prioritized list of small fixes.
```
