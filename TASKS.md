# Robotin Tasks

This file tracks small, safe, incremental tasks for Robotin.

Each task must be:

- small,
- implementable,
- testable,
- clearly useful,
- low-risk,
- aligned with `MASTER_PROMPT.md`,
- compatible with Windows development and future Raspberry Pi deployment.

## Task status values

Use one of:

- `pending`
- `in_progress`
- `done`
- `blocked`
- `review_needed`

---

## Task 001 - Project foundation

Status: done

### Goal

Create the minimal Python project foundation runnable on Windows.

### Scope

Included:

- Initial folder structure.
- `pyproject.toml`.
- `README.md`.
- `.env.example`.
- `RobotState` enum.
- Minimal state machine.
- Display interface.
- Mock display.
- Executable `main.py`.
- Minimal unit test for state transitions.

Out of scope:

- Real hardware.
- Real audio.
- Real AI.
- HTTP client.
- Wake word.
- Raspberry-specific setup.
- Docker.
- `systemd`.

### Acceptance criteria

- The project installs locally.
- `python -m robotin.main` runs on Windows.
- Robotin starts in `idle`.
- The mock display prints state changes.
- Unit tests pass.

### Recommended implementing agent

- `@scaffolder`

### Review agents

- `@tester`
- `@safety`

---

## Task 002 - Event model

Status: done

### Goal

Add a minimal internal event model for Robotin.

### Scope

Included:

- `src/robotin/events.py`.
- Event types for:
  - activation requested,
  - text received,
  - AI response received,
  - speech finished,
  - error occurred,
  - reset requested.
- Minimal tests for event creation.

Out of scope:

- Event bus.
- Async processing.
- Real microphone input.
- Real wake word.

### Acceptance criteria

- Events are simple, typed, and testable.
- No infrastructure dependencies are introduced.
- Tests pass.

### Recommended implementing agent

- `@domain`

### Review agents

- `@tester`
- `@safety`

---

## Task 003 - Application controller

Status: done

### Goal

Create a minimal `RobotController` that coordinates state changes and display updates.

### Scope

Included:

- `src/robotin/application/controller.py`.
- Controller uses state machine and display interface.
- Controller can transition through a simple text input flow using mocks.

Out of scope:

- Real AI client.
- Real TTS.
- Real microphone.
- Async event loop.

### Acceptance criteria

- Controller uses interfaces, not concrete hardware.
- State changes are reflected through the display interface.
- Tests verify the basic flow.

### Recommended implementing agent

- `@application`

### Review agents

- `@tester`
- `@safety`

---

## Task 004 - Mock AI client

Status: done

### Goal

Add an AI client interface and a deterministic mock implementation.

### Scope

Included:

- `src/robotin/interfaces/ai_client.py`.
- `src/robotin/infrastructure/ai_client_mock.py`.
- Tests for mock AI responses.

Out of scope:

- HTTP client.
- Real LLM.
- Internet access.
- Streaming responses.

### Acceptance criteria

- Application code can depend on the AI client interface.
- Mock AI client returns deterministic responses.
- Tests pass offline.

### Recommended implementing agent

- `@ai-client`

### Review agents

- `@tester`
- `@safety`

---

## Task 005 - Basic text conversation flow

Status: done

### Goal

Allow a simple console-based text interaction on Windows.

### Scope

Included:

- Update `main.py`.
- Use mock display.
- Use mock AI client.
- Move through:
  - `idle`
  - `listening`
  - `processing`
  - `speaking`
  - `idle`.

Out of scope:

- Real audio.
- Real TTS.
- Wake word.
- HTTP AI backend.

### Acceptance criteria

- Running `python -m robotin.main` starts an interactive console flow.
- User can type a message.
- Robotin produces a mock response.
- State changes are visible in the console.

### Recommended implementing agent

- `@application`

### Review agents

- `@tester`
- `@safety`

---

## Task 006 - Mock TTS

Status: done

### Goal

Add a TTS interface and a mock TTS implementation.

### Scope

Included:

- `src/robotin/interfaces/tts.py`.
- `src/robotin/infrastructure/tts_mock.py`.
- Controller can call TTS through the interface.
- Tests verify TTS was called.

Out of scope:

- Piper integration.
- Audio playback.
- Sound device configuration.

### Acceptance criteria

- TTS is decoupled behind an interface.
- Mock TTS works on Windows without audio hardware.
- Tests pass.

### Recommended implementing agent

- `@voice`

### Review agents

- `@tester`
- `@safety`

---

## Task 007 - Local HTTP AI client

Status: done

### Goal

Connect Robotin to a local AI backend over HTTP.

### Scope

Included:

- `src/robotin/infrastructure/ai_client_http.py`.
- Basic configuration for endpoint and timeout.
- Error handling.
- Tests using mocked HTTP behavior if practical.

Out of scope:

- Real LLM setup.
- Internet access.
- Streaming.
- Authentication.

### Acceptance criteria

- HTTP calls use explicit timeout.
- Failures return controlled errors or raise clear domain-safe exceptions.
- Runtime remains local-network/offline-first.
- Application logic still depends only on the AI client interface.

### Recommended implementing agent

- `@ai-client`

### Review agents

- `@tester`
- `@safety`

---

## Task 008 - Microphone and wake word mocks

Status: done

### Goal

Prepare microphone and wake word abstractions without requiring real audio hardware.

### Scope

Included:

- `src/robotin/interfaces/microphone.py`.
- `src/robotin/interfaces/wake_word.py`.
- `src/robotin/infrastructure/microphone_mock.py`.
- `src/robotin/infrastructure/wake_word_mock.py`.

Out of scope:

- `openWakeWord` real integration.
- Real microphone capture.
- Audio buffers.
- Continuous listening loop.

### Acceptance criteria

- Interfaces exist and are small.
- Mocks are deterministic.
- Tests pass without audio hardware.

### Recommended implementing agent

- `@voice`

### Review agents

- `@tester`
- `@safety`

---

## Backlog ideas

These are not initial tasks. Do not implement them until earlier tasks are stable.

- Piper TTS adapter.
- openWakeWord adapter.
- External local STT HTTP adapter.
- Local AI backend protocol document.
- Raspberry Pi display adapter.
- Raspberry Pi `systemd` service.
- Logging strategy.
- Configuration profiles for Windows and Raspberry Pi.
- Basic simulator for eyes and robot state.
- Error recovery policy.
- Offline model packaging strategy.
