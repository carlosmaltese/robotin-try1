# Robotin Architecture

Robotin uses a modular architecture designed to support development on Windows and later deployment on Raspberry Pi.

## Main idea

The project is divided into four main layers:

```text
domain
application
interfaces
infrastructure
```

The most important rule is:

```text
Domain and application code must not depend on real hardware, operating system details, audio libraries, HTTP clients, or Raspberry Pi-specific packages.
```

## Layers

### Domain

The domain layer contains pure robot logic.

Examples:

- robot states,
- transition rules,
- domain events,
- simple value objects.

The domain layer must be easy to test without mocks, hardware, network, or filesystem.

### Application

The application layer coordinates use cases.

Examples:

- handling a text interaction,
- moving through robot states,
- calling AI through an interface,
- calling TTS through an interface,
- updating the display through an interface.

The application layer depends on interfaces, not concrete adapters.

### Interfaces

The interfaces layer defines contracts.

Examples:

- display interface,
- microphone interface,
- TTS interface,
- AI client interface,
- wake word interface.

Interfaces must be small and implementation-independent.

### Infrastructure

The infrastructure layer contains concrete implementations.

Implemented now:

- mock display,
- mock TTS,
- mock AI client,
- local HTTP AI client,
- mock microphone,
- mock wake word detector.

Planned later:

- Raspberry Pi display adapter,
- Piper TTS adapter,
- openWakeWord adapter.

Only this layer may depend on real hardware libraries or external integration packages.

## Initial interaction flow

The initial basic flow is:

```text
idle
  ↓
listening
  ↓
processing
  ↓
speaking
  ↓
idle
```

In the first phase, this flow is driven by console input and mock implementations.

## Future hardware migration

The project should support this migration path:

```text
Windows + mocks
  ↓
Windows + local AI HTTP backend
  ↓
Raspberry Pi 4 + real display/audio adapters
  ↓
Raspberry Pi 5 + same logical architecture
```

The migration should mostly involve adding or replacing infrastructure adapters, not rewriting domain or application logic.

## Dependency direction

Allowed dependency direction:

```text
application → domain
application → interfaces
infrastructure → interfaces
infrastructure → domain when needed
main → application
main → infrastructure
```

Forbidden dependency direction:

```text
domain → infrastructure
domain → HTTP/audio/GPIO
application → concrete hardware libraries
interfaces → infrastructure
```

## Entry point

The main entry point should be:

```text
python -m robotin.main
```

`main.py` may wire concrete implementations together, but core logic should live elsewhere.

## Configuration

Configuration should start simple.

Initial options:

- `.env`
- `.env.example`
- simple config module

Do not introduce complex configuration frameworks early.

## Display rendering ownership

`RobotController` is solely responsible for calling `display.show_state()` after every state transition. `main.py` does not render state directly.

## Error responsibilities

`RobotController` logs AI client failures but re-raises the exception unchanged. `recover_to_idle_after_error` in `runtime.py` is the single point responsible for moving the state machine to `ERROR` and back to `IDLE`. This keeps error recovery centralized and testable.

## Testing strategy

Initial tests should focus on:

- state transitions,
- controller behavior,
- mock adapters,
- error handling,
- interface-driven design.

Current test coverage includes deterministic tests for state machine, events, controller flow, mock AI/TTS/microphone/wake-word adapters, and local HTTP AI adapter behavior.

Hardware tests come later and must be separated from normal Windows tests.
