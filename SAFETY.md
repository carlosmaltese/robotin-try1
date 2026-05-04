# Robotin Safety Rules

Robotin is a physical robot project. Even if the first implementation uses only mocks, the architecture must assume that future code may control real hardware.

## Core safety principles

- No real hardware control without explicit human approval.
- No direct hardware access from domain or application layers.
- All hardware-specific code must live under `src/robotin/infrastructure/`.
- Keep mock implementations available for Windows development.
- Prefer safe defaults.
- Fail clearly and return to a safe state when possible.
- Avoid uncontrolled loops, blocking calls, and hidden background behavior.

## Layer safety rules

### Domain layer

The domain layer must not:

- import hardware libraries,
- perform I/O,
- access the network,
- access files,
- use threads,
- use timers,
- call audio APIs,
- call HTTP APIs.

The domain layer may:

- define robot states,
- validate transitions,
- define events,
- define pure logic.

### Application layer

The application layer must not:

- call GPIO directly,
- call audio libraries directly,
- call HTTP clients directly,
- depend on concrete infrastructure implementations.

The application layer may:

- orchestrate use cases,
- call interfaces,
- handle high-level robot flow,
- move the robot between states,
- handle controlled errors.

### Infrastructure layer

The infrastructure layer may:

- implement hardware adapters,
- implement mock adapters,
- implement HTTP clients,
- implement audio integrations,
- implement Raspberry Pi integrations.

The infrastructure layer must:

- use explicit timeouts for external calls,
- handle errors clearly,
- avoid unsafe assumptions,
- expose simple behavior through interfaces.

## State safety rules

Robotin has these initial states:

- `idle`
- `listening`
- `processing`
- `speaking`
- `error`

Rules:

- Robotin should start in `idle`.
- Robotin should return to `idle` after a successful interaction.
- Robotin should move to `error` when unrecoverable behavior happens.
- Robotin should have a reset path from `error` to `idle`.
- Transitions should be explicit and testable.

## External call safety rules

Any external call must have:

- explicit timeout,
- clear error handling,
- no dependency on internet access for normal runtime,
- testable behavior with a mock or fake implementation.

Examples of external calls:

- local HTTP AI backend,
- STT server,
- TTS engine,
- microphone capture,
- display hardware,
- Raspberry Pi GPIO,
- serial communication.

## Loop safety rules

Avoid infinite loops unless they include:

- a clear stop condition,
- small sleep or blocking wait,
- error handling,
- graceful shutdown,
- testable boundaries.

Initial tasks should avoid continuous loops unless absolutely needed.

## Audio safety rules

Before real audio integration:

- keep microphone mocked,
- keep TTS mocked,
- avoid requiring audio hardware for tests,
- avoid background recording by default,
- make activation explicit.

When real audio is added:

- isolate it behind interfaces,
- document required devices,
- handle missing devices gracefully.

## AI behavior safety rules

Robotin is child-friendly.

AI responses should eventually be filtered or constrained to be:

- age-appropriate,
- calm,
- non-threatening,
- non-manipulative,
- privacy-conscious,
- safe for a child interaction context.

Initial mock AI responses should be neutral and simple.

## Hardware safety rules for future phases

Before connecting motors, servos, LEDs, relays, or physical actuators:

- add explicit limits,
- add timeouts,
- add a safe stop mechanism,
- add a manual emergency stop if movement or electrical switching is involved,
- test with mocks first,
- test with low power or disconnected load first,
- review all code manually.

## Agent safety rules

AI coding agents may:

- create code,
- modify files,
- write tests,
- write documentation,
- propose adapters.

AI coding agents must not:

- execute code that controls real hardware without human approval,
- remove safety checks,
- bypass interfaces,
- introduce hidden network dependencies,
- introduce always-on recording without explicit approval,
- create uncontrolled background processes.

## Safety review checklist

Before merging a task, check:

- Does the code keep hardware out of domain/application layers?
- Does every external call have a timeout?
- Can the feature be tested on Windows?
- Are mocks still available?
- Are state transitions explicit?
- Is error behavior clear?
- Are dependencies minimal?
- Is future Raspberry Pi migration preserved?
