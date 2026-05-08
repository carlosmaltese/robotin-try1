# Robotin Remedy Tasks

Remedial work that must be completed **before** starting Task 009 (or any
new feature task). These tasks address defects and quality gaps detected in
`Revision02.md` against the codebase at commit
`d8b5f56 - Harden HTTP AI client error handling`.

Each remedy task follows the same conventions as `TASKS.md`:

- small, implementable, testable, low-risk,
- aligned with `MASTER_PROMPT.md`, `AGENTS.md`, `SAFETY.md`,
- compatible with Windows development and future Raspberry Pi deployment.

## Status values

`pending`, `in_progress`, `done`, `blocked`, `review_needed`.

## Execution order

Run remedies in numerical order. Some have explicit dependencies — those are
declared in the **Depends on** field.

```text
R-001 → R-002 → R-003 → R-004 → R-005 → R-006 → R-007 → R-008 → R-009 → R-010 → R-011
```

After all remedies are `done`, the project is ready to define Task 009.

---

## R-001 - Sync protocol documentation with `HTTPAIClient`

Status: done
Depends on: none
Defect: D-01

### Goal

Make `docs/protocol.md` describe the actual wire format used by
`HTTPAIClient`, so a future backend implementer cannot be misled by the
document.

### Scope

Included:

- Update `docs/protocol.md` so request shape is `{"text": "..."}` and
  response shape is `{"response": "..."}`.
- Add an explicit note: "This document mirrors
  `src/robotin/infrastructure/ai_client_http.py`. Keep them in sync."
- No code changes.

Out of scope:

- Changing the wire format.
- Adding new endpoints or fields.
- Streaming or authentication.

### Files to modify

- `docs/protocol.md`

### Acceptance criteria

- The request and response examples in `docs/protocol.md` exactly match
  what `HTTPAIClient.generate_response` sends and parses.
- Tests still pass without modification (no code changed).

### Recommended agent

- `@docs`

### Review agents

- `@safety`

---

## R-002 - Validate URL scheme in `HTTPAIClient`

Status: done
Depends on: none
Defect: D-03

### Goal

Reject `base_url` values whose scheme is not `http` or `https`, so a
misconfigured environment cannot turn an AI call into a `file://` read or
another unsafe scheme.

### Scope

Included:

- In `HTTPAIClient.__init__`, parse `base_url` with `urllib.parse.urlsplit`
  and raise `ValueError` if `scheme` is not `http` or `https`, or if
  `netloc` is empty.
- Add a test for each rejected scheme (`file://`, empty, no scheme).
- Add a test confirming `https://...` is accepted.

Out of scope:

- Allowlists of hostnames.
- TLS verification configuration.
- Proxy support.

### Files to create or modify

- `src/robotin/infrastructure/ai_client_http.py`
- `tests/test_ai_client_http.py`

### Acceptance criteria

- `HTTPAIClient(base_url="file:///etc/passwd")` raises `ValueError`.
- `HTTPAIClient(base_url="not-a-url")` raises `ValueError`.
- `HTTPAIClient(base_url="https://localhost")` constructs successfully.
- All existing tests still pass.

### Recommended agent

- `@ai-client`

### Review agents

- `@tester`
- `@safety`

---

## R-003 - Centralized configuration module (`config.py`) with `.env` loader

Status: done
Depends on: R-002
Defect: D-02 + Revision 01 gap

### Goal

Provide a single place to load configuration, including a minimal stdlib
`.env` parser, so that copying `.env.example` to `.env` actually changes
runtime behavior.

### Scope

Included:

- New `src/robotin/config.py` exposing a frozen dataclass
  `RobotinConfig` with at least:
  - `ai_base_url: str`
  - `ai_timeout_seconds: float`
- Function `load_config(env_file: Path | None = None) -> RobotinConfig`:
  - reads `.env` from project root if it exists,
  - falls back to process environment variables,
  - falls back to documented defaults.
- `.env` parser must be stdlib-only, ignore comments and blank lines, and
  not override variables already exported in the shell.
- Update `HTTPAIClient` to optionally accept a `RobotinConfig` (keep
  current `base_url` / `timeout_seconds` parameters for backward
  compatibility within tests).
- Update `main.py` to call `load_config()` once and pass values down.
- Tests for: `.env` parsing, fallback to env vars, fallback to defaults,
  comment/blank-line handling, env-var-takes-precedence rule.

Out of scope:

- Multiple configuration profiles (Windows vs Raspberry Pi).
- YAML / TOML configuration.
- Hot-reload.

### Files to create or modify

- `src/robotin/config.py` (new)
- `src/robotin/infrastructure/ai_client_http.py`
- `src/robotin/main.py`
- `tests/test_config.py` (new)
- `tests/test_ai_client_http.py` (only if needed to keep passing)

### Acceptance criteria

- A `.env` next to `pyproject.toml` is loaded automatically.
- Variables already set in the shell win over `.env` values.
- All existing tests still pass.
- New tests cover the parser and precedence rules.

### Recommended agent

- `@scaffolder` (creates module) + `@ai-client` (rewires HTTP client)

### Review agents

- `@tester`
- `@safety`

---

## R-004 - Logging strategy

Status: done
Depends on: R-003
Defect: Revision 01 gap (preparation for R-005)

### Goal

Replace ad-hoc `print()` calls with the standard `logging` module so that
the next remedy (R-005) can replace `pass` with a real log line, and so
future infrastructure can add structured logs without coupling to stdout.

### Scope

Included:

- Configure a project logger `robotin` in a small helper, called from
  `main.py` once.
- Default level: `INFO`. Configurable via `RobotinConfig` (new field
  `log_level: str`, default `"INFO"`).
- Replace `print` calls in:
  - `src/robotin/main.py` (status messages keep going to stdout via
    `output_func`, but operational messages use the logger),
  - `src/robotin/application/runtime.py`,
  - `src/robotin/infrastructure/display_mock.py` (logger at `INFO`,
    keep deterministic by injecting a logger or capturing via `caplog` in
    tests).
- Update tests to use `caplog` fixture instead of `capsys` for log lines.

Out of scope:

- File handlers, rotation, JSON logs.
- Per-module log levels beyond the project root logger.

### Files to create or modify

- `src/robotin/config.py`
- `src/robotin/main.py`
- `src/robotin/application/runtime.py`
- `src/robotin/infrastructure/display_mock.py`
- `tests/test_runtime.py`
- `tests/test_controller.py` (if it asserted on display stdout)
- `tests/test_main.py`

### Acceptance criteria

- No production module under `src/robotin/` calls `print` directly except
  the conversational user-facing `output_func` path in `main.py`.
- All existing behavior is preserved; tests pass.
- Setting `ROBOTIN_LOG_LEVEL=DEBUG` produces DEBUG output without code
  changes.

### Recommended agent

- `@infrastructure`

### Review agents

- `@tester`
- `@safety`

---

## R-005 - Replace silent `pass` in error recovery

Status: done
Depends on: R-004
Defect: D-04

### Goal

Stop swallowing `ValueError` in `recover_to_idle_after_error` so that any
future invalid transition surfaces in logs instead of being hidden.

### Scope

Included:

- In `src/robotin/application/runtime.py:46-48`, replace
  `except ValueError: pass` with a logger warning that includes the
  current state and the attempted transition.
- Add a test that triggers the branch (e.g. by forcing
  `runtime.state_machine` into a state where `→ ERROR` is not allowed
  using a stub) and asserts the warning is recorded with `caplog`.

Out of scope:

- Changing the recovery semantics.
- Adding new states.

### Files to modify

- `src/robotin/application/runtime.py`
- `tests/test_runtime.py`

### Acceptance criteria

- The `pass` branch is gone.
- A warning is emitted on the project logger when transition to `ERROR`
  fails.
- New test asserts the warning is recorded.

### Recommended agent

- `@application`

### Review agents

- `@tester`
- `@safety`

---

## R-006 - Remove duplicate initial `show_state` and clarify ownership

Status: done
Depends on: none
Defect: D-05

### Goal

Decide once whether `main.py` or `RobotController` is responsible for
showing the initial `IDLE` state, eliminate the duplicated call, and
document the rule.

### Scope

Included:

- Remove the redundant `show_state` from either `main.py:23` or the final
  step of `controller.handle_text_turn`. Recommended choice: keep the
  initial render in `main.py` (boot state) and keep the per-turn renders
  inside the controller — already the case — but stop the controller from
  duplicating IDLE on the very first turn by checking that the previous
  state changed before calling `show_state`. Alternative: drop the
  initial render in `main.py` and let the first turn produce all renders.
- Add a short note to `docs/architecture.md` describing which layer owns
  initial display rendering.
- Update tests if any assertion depended on the duplicated output.

Out of scope:

- Refactoring the controller to a pub/sub model.
- Adding event-driven display updates.

### Files to modify

- `src/robotin/main.py` or `src/robotin/application/controller.py`
  (one of the two)
- `docs/architecture.md`
- `tests/test_controller.py` (only if needed)

### Acceptance criteria

- Running `python -m robotin.main` and entering one message produces a
  single `state=idle` line at boot, then `listening`, `processing`,
  `speaking`, `idle` once each per turn.
- Tests pass and reflect the new expected sequence.

### Recommended agent

- `@application`

### Review agents

- `@tester`
- `@docs`

---

## R-007 - Expose `ai_client` and `tts` on `RobotRuntime`

Status: done
Depends on: none
Defect: D-06

### Goal

Make `RobotRuntime` a complete dependency container so future tasks can
reach the AI client and TTS without re-wiring at the call site.

### Scope

Included:

- Add `ai_client: AIClient` and `tts: TTS | None` fields to
  `RobotRuntime` (`src/robotin/application/runtime.py`).
- Update `create_runtime` to populate them.
- Add a test asserting that `runtime.ai_client` and `runtime.tts` are the
  exact instances passed in.

Out of scope:

- Adding more fields than `ai_client` and `tts`.
- Changing constructor signatures of `RobotController`.

### Files to modify

- `src/robotin/application/runtime.py`
- `tests/test_runtime.py`

### Acceptance criteria

- `runtime.ai_client is ai_client` and `runtime.tts is tts` (or
  `runtime.tts is None`).
- All existing tests pass.

### Recommended agent

- `@application`

### Review agents

- `@tester`

---

## R-008 - Document `AIClient` failure contract and decide controller policy

Status: done
Depends on: R-004
Defect: D-07

### Goal

Make the failure contract of `AIClient.generate_response` explicit, and
decide whether `RobotController` should translate failures into a state
transition or continue letting `main.py` handle recovery.

### Scope

Included:

- Update the docstring on `src/robotin/interfaces/ai_client.py` to state:
  - implementations may raise; the only documented exception type today is
    `HTTPAIClientError`,
  - callers must not assume `generate_response` is total.
- In `RobotController.handle_text_turn`, wrap the call to
  `self._ai_client.generate_response(user_text)` so that on failure:
  - the controller logs a warning with the project logger,
  - re-raises the original exception, OR transitions to `ERROR` and
    re-raises (decision below).
- Decision: re-raise after logging. Keep `recover_to_idle_after_error`
  responsible for moving to `ERROR` and back to `IDLE`. Document this in
  `docs/architecture.md` under a new "Error responsibilities" subsection.
- Add a test where `AIClient.generate_response` raises and the controller
  re-raises the same exception type.

Out of scope:

- Retry / backoff logic.
- Alternative AI client fallbacks.

### Files to modify

- `src/robotin/interfaces/ai_client.py`
- `src/robotin/application/controller.py`
- `docs/architecture.md`
- `tests/test_controller.py`

### Acceptance criteria

- Docstring on the interface lists failure modes.
- Controller test confirms exceptions from the AI client propagate.
- Architecture doc has a clear "who handles errors" section.

### Recommended agent

- `@application` + `@docs`

### Review agents

- `@tester`
- `@safety`

---

## R-009 - Test coverage for state transitions and error paths

Status: done
Depends on: R-005, R-006, R-008
Quality gap: Q-03

### Goal

Close the test holes left after the previous remedies and the original
suite, so any future regression is caught.

### Scope

Included, in `tests/test_state_machine.py`:

- Test `ERROR → IDLE` directly.
- Test invalid transitions originating from `LISTENING`, `PROCESSING`, and
  `SPEAKING` (one assertion per source state).

In `tests/test_main.py`:

- Test that an exception raised by the AI client during a turn is caught
  by the loop, triggers `recover_to_idle_after_error`, and the loop
  continues to accept the next input.

Out of scope:

- Property-based tests.
- Coverage reporting tooling.

### Files to modify

- `tests/test_state_machine.py`
- `tests/test_main.py`

### Acceptance criteria

- All new tests pass.
- Total test count increases by at least 5 cases.

### Recommended agent

- `@tester`

### Review agents

- `@safety`

---

## R-010 - Linter and formatter baseline

Status: done
Depends on: R-001…R-009
Quality gap: Q-01

### Goal

Lock in a consistent style baseline so future agent-driven edits do not
churn formatting.

### Scope

Included:

- Add `ruff` to `[project.optional-dependencies] dev` in
  `pyproject.toml`.
- Add a `[tool.ruff]` section with line length 100 and the rule sets
  `E`, `F`, `I`, `B`, `UP`. Target `py311`.
- Run `ruff check --fix` and `ruff format` once, commit the result as a
  separate commit.
- Add a `make lint` style entry or document the command in
  `docs/development.md`.

Out of scope:

- `mypy` strict mode (deferred).
- Pre-commit hooks (deferred).

### Files to modify

- `pyproject.toml`
- `docs/development.md`
- Any source file the formatter touches.

### Acceptance criteria

- `ruff check src tests` exits 0.
- `ruff format --check src tests` exits 0.
- All tests still pass.

### Recommended agent

- `@scaffolder`

### Review agents

- `@safety`

---

## R-011 - Continuous integration

Status: done
Depends on: R-010
Quality gap: Q-02

### Goal

Run the test suite and the linter on every push and pull request so
remedies stay enforced.

### Scope

Included:

- New `.github/workflows/ci.yml` with one job:
  - matrix: `python-version: ["3.11", "3.12"]`,
  - steps: checkout, setup-python, `pip install -e .[dev]`,
  - `ruff check .`,
  - `ruff format --check .`,
  - `pytest -q`.
- Document the CI badge URL in `README.md` (optional).

Out of scope:

- Coverage upload services.
- Release automation.
- Cache configuration tuning.

### Files to create or modify

- `.github/workflows/ci.yml` (new)
- `README.md` (optional badge)

### Acceptance criteria

- Workflow file is syntactically valid YAML.
- Pushing a branch triggers the workflow and it passes on a clean tree.

### Recommended agent

- `@scaffolder`

### Review agents

- `@safety`

---

## After remedies are complete

Once R-001…R-011 are all `done`:

- The defects D-01…D-07 from `Revision02.md` are resolved.
- The quality gaps Q-01…Q-04 from `Revision02.md` are resolved.
- Documentation, code, and configuration are consistent.
- A green CI run protects the new baseline.

At that point, define **Task 009** in `TASKS.md` (next feature task — see
Phase C/D in `Revision02.md` §6 for candidates: STT interface + mock,
event bus, Piper TTS adapter).
