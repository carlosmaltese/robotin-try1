# Robotin Technical Decisions

This file records important technical decisions for Robotin.

Use this format for new decisions:

```md
## ADR-XXX - Title

Date:
YYYY-MM-DD

Status:
Accepted / Proposed / Superseded

Decision:
What was decided.

Reason:
Why this decision was made.

Consequences:
What this enables, limits, or implies.
```

---

## ADR-001 - Main language

Date:
2026-05-04

Status:
Accepted

Decision:
Use Python as the main language for Robotin.

Reason:
Python is simple, productive, portable between Windows and Raspberry Pi OS, and suitable for audio, local AI integration, and hardware adapters.

Consequences:
Python will be used for the base robot brain, state machine, interfaces, mocks, local adapters, and initial integrations.

---

## ADR-002 - Architecture style

Date:
2026-05-04

Status:
Accepted

Decision:
Use a modular architecture with domain, application, interfaces, and infrastructure layers.

Reason:
This keeps robot logic independent from hardware and makes Windows development with mocks possible.

Consequences:
Domain and application code must not directly depend on hardware libraries, HTTP clients, audio APIs, or Raspberry Pi-specific packages.

---

## ADR-003 - Hardware integration strategy

Date:
2026-05-04

Status:
Accepted

Decision:
Use mock implementations first, then add real hardware adapters later.

Reason:
The project must be developed and tested on Windows before connecting real hardware.

Consequences:
Every real hardware feature must have an interface and a mock implementation.

---

## ADR-004 - Initial runtime target

Date:
2026-05-04

Status:
Accepted

Decision:
Use Windows + VS Code as the initial development environment and Raspberry Pi OS Lite 64-bit as the later deployment target.

Reason:
This supports fast development while preserving the final embedded deployment path.

Consequences:
Code must avoid platform-specific assumptions unless isolated in infrastructure adapters.

---

## ADR-005 - Dependency strategy

Date:
2026-05-04

Status:
Accepted

Decision:
Prefer the Python standard library first. Add third-party dependencies only when clearly justified.

Reason:
Robotin will eventually run on Raspberry Pi, where simplicity, resource usage, and maintainability matter.

Consequences:
Initial tasks should avoid dependencies beyond minimal development tools such as `pytest`.

---

## ADR-006 - Offline-first runtime

Date:
2026-05-04

Status:
Accepted

Decision:
Robotin runtime behavior must be offline-first.

Reason:
The final system must work without internet dependency.

Consequences:
AI, STT, and TTS integrations should target local services or local models. Internet APIs must not be required for normal operation.

---

## ADR-007 - Local AI backend strategy

Date:
2026-05-04

Status:
Accepted

Decision:
Use a mock AI client first, then a local HTTP AI client.

Reason:
This allows the robot brain to be developed before the final local model runtime is chosen.

Consequences:
Application logic must depend on an `AIClient` interface, not on a concrete HTTP implementation.

---

## ADR-008 - No Docker at the beginning

Date:
2026-05-04

Status:
Accepted

Decision:
Do not introduce Docker in the initial phase.

Reason:
The first goal is to create a lightweight, testable, local foundation without unnecessary operational complexity.

Consequences:
Initial setup should work with a local Python virtual environment and `pyproject.toml`.

---

## ADR-009 - No direct hardware control from agents

Date:
2026-05-04

Status:
Accepted

Decision:
AI coding agents must not be allowed to directly control real hardware.

Reason:
Robotin may later include physical components. Safety requires human review before hardware execution.

Consequences:
Agents may generate code, mocks, tests, and adapters, but real hardware execution must be manually reviewed and explicitly run by the human developer.
