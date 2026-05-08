# Revision 01 - Robotin Project Analysis

> Initial code review and architecture analysis of the Robotin project.
>
> **Reviewer:** Carlos Maltese
> **Review date:** 2026-05-08
> **Repository:** https://github.com/carlosmaltese/robotin

> **Last analyzed commit:** `d8b5f56 - Harden HTTP AI client error handling`

---

## 1. Project overview

**Robotin** is a small child-friendly robot project (~15-20 cm tall) designed
to interact with a child. The codebase is a **Python "robot brain"** in early
development phase, fully driven by mocks, with a clear migration path to
Raspberry Pi 4 → Raspberry Pi 5.

- **Language:** Python `>=3.11`
- **Runtime dependencies:** none (only standard library)
- **Dev dependencies:** `pytest>=8.0`
- **Target dev environment:** Windows + VS Code
- **Target deployment:** Raspberry Pi OS Lite 64-bit
- **Status:** 8 tasks completed (`Task 001` → `Task 008`), all marked as `done`.

---

## 2. Architecture

The project follows a strict **Clean Architecture** with 4 layers and a clear
dependency direction:

```text
main → application → domain
            ↓
       interfaces
            ↑
     infrastructure
```

| Layer            | Responsibility                                  | Rules                                          |
| ---------------- | ----------------------------------------------- | ---------------------------------------------- |
| `domain/`        | Pure robot logic (states, events).              | No I/O, no network, no hardware imports.       |
| `application/`   | Use case orchestration.                         | Only depends on interfaces.                    |
| `interfaces/`    | Abstract contracts (ABC).                       | No concrete implementations.                   |
| `infrastructure/`| Concrete adapters (mocks, HTTP).                | Only layer allowed to use external libraries.  |

The architectural rule is enforced both in `MASTER_PROMPT.md` and `SAFETY.md`,
and verified by the actual code structure.

---

## 3. Source tree

```text
src/robotin/
├── main.py                          # Console entrypoint
├── state_machine.py                 # FSM with allowed transitions
├── events.py                        # Event dataclasses
├── domain/
│   └── robot_state.py               # RobotState enum
├── application/
│   ├── controller.py                # RobotController (orchestration)
│   └── runtime.py                   # Runtime wiring + error recovery
├── interfaces/
│   ├── display.py                   # Display ABC
│   ├── ai_client.py                 # AIClient ABC
│   ├── tts.py                       # TTS ABC
│   ├── microphone.py                # Microphone ABC
│   └── wake_word.py                 # WakeWordDetector ABC
└── infrastructure/
    ├── display_mock.py              # Console display mock
    ├── ai_client_mock.py            # Deterministic AI mock
    ├── ai_client_http.py            # Local HTTP AI client (urllib)
    ├── tts_mock.py                  # Mock TTS recording calls
    ├── microphone_mock.py           # Mock microphone with input list
    └── wake_word_mock.py            # Mock wake word detector
```

---

## 4. Key components

### 4.1 State machine

Strict FSM with explicit allowed transitions. Any disallowed transition raises
`ValueError`, which guarantees safe state behavior.

Allowed transitions:

| From         | To                          |
| ------------ | --------------------------- |
| `IDLE`       | `LISTENING`, `ERROR`        |
| `LISTENING`  | `PROCESSING`, `ERROR`       |
| `PROCESSING` | `SPEAKING`, `ERROR`         |
| `SPEAKING`   | `IDLE`, `ERROR`             |
| `ERROR`      | `IDLE`                      |

### 4.2 RobotController (`application/controller.py`)

Orchestrates the full flow `idle → listening → processing → speaking → idle`
using **constructor-based dependency injection** through interfaces only. The
`tts` parameter is optional (`TTS | None`), which keeps the controller usable
without speech output.

### 4.3 HTTP AI client (`infrastructure/ai_client_http.py`)

Robust local HTTP client based on `urllib` (no third-party dependencies):

- Explicit timeout (configurable via env var `ROBOTIN_AI_TIMEOUT_SECONDS`).
- Differentiated error handling:
  - `HTTPError`
  - `socket.timeout`
  - `TimeoutError`
  - `URLError`
  - Invalid JSON
  - Missing or empty `response` field
- Typed exception `HTTPAIClientError`.
- Validates `timeout > 0` at construction time.

### 4.4 Runtime + recovery (`application/runtime.py`)

Cleanly separates the wiring from `main.py`. The function
`recover_to_idle_after_error` guarantees that any unexpected exception leads
the robot back to `idle` safely, while reflecting the state change through the
display interface.

### 4.5 Events (`events.py`)

Six frozen dataclasses representing domain events:

- `ActivationRequestedEvent`
- `TextReceivedEvent`
- `AIResponseReceivedEvent`
- `SpeechFinishedEvent`
- `ErrorOccurredEvent`
- `ResetRequestedEvent`

Currently defined and tested, but **not yet wired** into the controller flow.

---

## 5. Tests

8 deterministic test files, all running on the standard library plus
`pytest` and `unittest.mock`.

| Test file                                | Coverage                                                                 |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| `test_state_machine.py`                  | Valid and invalid transitions.                                           |
| `test_events.py`                         | Event creation and typing.                                               |
| `test_controller.py`                     | Full flow + TTS mock integration + deterministic fallback.               |
| `test_ai_client_mock.py`                 | Predefined response, fallback, empty input.                              |
| `test_ai_client_http.py`                 | Success, URLError, HTTPError, socket timeout, invalid JSON, missing field, non-positive timeout. |
| `test_microphone_wake_word_mocks.py`     | Deterministic mock behavior for mic and wake word.                       |
| `test_runtime.py`                        | Runtime wiring + safe error recovery path.                               |
| `test_main.py`                           | Clean exit when user types `exit`.                                       |

All tests are deterministic and require no hardware.

---

## 6. Configuration

- `pyproject.toml` declares package, optional `dev` dependencies, pytest
  config (`pythonpath = ["src"]`, `testpaths = ["tests"]`).
- `.env.example` exposes:
  - `ROBOTIN_AI_BASE_URL`
  - `ROBOTIN_AI_TIMEOUT_SECONDS`
- `.gitignore` covers Python build artifacts, virtualenv, caches, `.env`,
  and `.vscode/`.

---

## 7. Documentation

The project is **document-governed**, with consistent rules across files:

| File                       | Purpose                                                                |
| -------------------------- | ---------------------------------------------------------------------- |
| `README.md`                | Project description, goals, architecture summary, current status.      |
| `MASTER_PROMPT.md`         | Master prompt with non-negotiable architectural rules.                 |
| `AGENTS.md`                | Subagent roles: architect, scaffolder, domain, application, hardware-abstraction, infrastructure, voice, ai-client, tester, safety, docs. |
| `TASKS.md`                 | Incremental task backlog with explicit acceptance criteria.            |
| `DECISIONS.md`             | 9 ADRs with the format decision + reason + consequences.               |
| `SAFETY.md`                | Per-layer safety rules and external call discipline.                   |
| `docs/architecture.md`     | Detailed architecture description.                                     |
| `docs/development.md`      | Local development workflow.                                            |
| `docs/protocol.md`         | Future protocol notes (AI, STT, hardware).                             |
| `docs/raspberry_setup.md`  | Placeholder for future Raspberry Pi setup notes.                       |

---

## 8. Strengths

1. **Strong architectural discipline:** layer separation is strict and
   actually respected by the code.
2. **Zero runtime dependencies:** maximum portability between Windows and
   Raspberry Pi.
3. **Deterministic, fast tests** without hardware requirements.
4. **Explicit error handling** with timeouts on every external call.
5. **Extensive documentation** that stays consistent with the implementation.
6. **Mock-first philosophy** correctly applied across every external
   capability.
7. **Single console entrypoint** `python -m robotin.main` keeps the runtime
   surface small.

---

## 9. Gaps and improvement opportunities

Comparing the planned structure in `MASTER_PROMPT.md` against the current
implementation:

| Missing item                              | Notes                                                                                  |
| ----------------------------------------- | -------------------------------------------------------------------------------------- |
| `src/robotin/config.py`                   | Listed in target structure, not yet created. Env var loading is currently scattered inside `ai_client_http.py`. |
| `assets/sounds/` and `assets/eyes/`       | Planned folders, not created yet.                                                      |
| Event bus / event loop                    | Events are defined but not consumed by the controller flow.                            |
| Real adapters                             | Piper TTS, openWakeWord, Raspberry Pi display — still in backlog.                      |
| STT interface                             | Not defined yet (no `interfaces/stt.py`, no STT mock).                                 |
| Logging strategy                          | Currently uses `print()`. Listed in the backlog.                                       |
| Reset path from `ERROR`                   | Exists in the state machine but `ResetRequestedEvent` is not wired to a controller path. |
| Configuration profiles                    | Single `.env` only. No Windows vs Raspberry Pi separation yet.                         |

---

## 10. Recommended next tasks

Aligned with `TASKS.md` backlog and the gaps above, listed by priority:

1. **Task 009 - Centralized configuration module (`config.py`)**
   Reason: avoid scattered `os.getenv` calls and prepare a single place for
   future Windows vs Raspberry Pi configuration profiles.

2. **Task 010 - STT interface + mock**
   Reason: complete the voice abstraction trio (microphone + wake word + STT)
   before integrating any real audio adapter.

3. **Task 011 - Logging strategy**
   Reason: replace `print()` with `logging` in infrastructure and main, while
   keeping mocks deterministic for tests.

4. **Task 012 - Reset/error event path wiring**
   Reason: connect `ResetRequestedEvent` to the controller so the recovery
   path is exercised by application logic, not only by the runtime helper.

5. **Backlog candidates (Piper TTS, openWakeWord)**
   Reason: only after the configuration and logging foundations are in place,
   so the first real adapters land on a solid base.

---

## 11. Summary

The project is small, focused, well-documented, and architecturally
disciplined. It is in an excellent state to start adding real adapters in a
controlled way, with no apparent technical debt and strong safety
foundations in place.
