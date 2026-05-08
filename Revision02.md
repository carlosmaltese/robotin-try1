# Revision 02 - Robotin Project Analysis

> Combined review: structural gaps from Revision 01 plus real defects detected
> in the existing code. Builds on `Revision01.md`, does not replace it.
>
> **Reviewer:** Carlos Maltese (with assisted code review)
> **Review date:** 2026-05-08
> **Repository:** https://github.com/carlosmaltese/robotin
> **Last analyzed commit:** `d8b5f56 - Harden HTTP AI client error handling`

---

## 1. Scope of this revision

`Revision01.md` is an excellent inventory of what exists and what is missing
from the planned structure, but it does not flag defects in the code that is
already merged. This document adds:

- **Real defects** in current code (with `file:line` references).
- **Risks** that contradict `SAFETY.md` despite passing tests.
- **Quality / process gaps** (lint, CI, test coverage holes).
- A **prioritized fix-and-build plan** that attacks defects before adding new
  features.

Findings from Revision 01 that remain valid are referenced, not duplicated.

---

## 2. Defects in existing code

### D-01 - Documented protocol does not match `HTTPAIClient` wire format

- `docs/protocol.md:17-34` documents request `{"input": "..."}` and response
  `{"text": "..."}`.
- `src/robotin/infrastructure/ai_client_http.py:28` sends `{"text": "..."}`.
- `src/robotin/infrastructure/ai_client_http.py:58` reads `{"response": "..."}`.

Anyone implementing the local AI backend by reading the docs will produce a
server that the client cannot talk to. This contradicts `Revision01.md` §8
which claims documentation is consistent with implementation.

**Fix options:** update `docs/protocol.md` to reflect the actual wire format,
or change the client to use the documented one. Recommended: update the doc,
since the implementation has tests covering the current shape.

### D-02 - `.env.example` is never loaded at runtime

- `.env.example` advertises `ROBOTIN_AI_BASE_URL` and
  `ROBOTIN_AI_TIMEOUT_SECONDS`.
- No module parses a `.env` file. `HTTPAIClient.__init__`
  (`src/robotin/infrastructure/ai_client_http.py:19-22`) only reads
  `os.getenv`, which requires the variable to be exported in the shell.

A user who copies `.env.example` to `.env` and runs `python -m robotin.main`
will silently get the defaults. Solvable without dependencies via a small
`.env` parser inside the future `config.py`.

### D-03 - `HTTPAIClient` does not validate the URL scheme

- `src/robotin/infrastructure/ai_client_http.py:19,30-35` accepts any
  `base_url` and passes it directly to `urllib.request.urlopen`.
- `urllib` honors `file://`, `ftp://` and other schemes. A misconfigured env
  var or future config file could turn an HTTP call into a local file read.

This contradicts `SAFETY.md` ("prefer safe defaults", "explicit error
handling for external calls"). Mitigation is small: reject any scheme other
than `http` / `https` at construction time.

### D-04 - `recover_to_idle_after_error` swallows `ValueError`

- `src/robotin/application/runtime.py:46-48`:

  ```python
  try:
      runtime.state_machine.transition_to(RobotState.ERROR)
  except ValueError:
      pass
  ```

Today the only path that raises is "already in `ERROR`", which is benign.
But if a future change adds a state without updating
`StateMachine._ALLOWED_TRANSITIONS`, this `pass` will hide it. Should at
least log the failure.

### D-05 - Double `show_state(IDLE)` on startup

- `src/robotin/main.py:23` shows the initial `IDLE` state.
- The first `handle_text_turn` call also ends by transitioning back to
  `IDLE` and calling `show_state` (`controller.py:35-36`).

Result: on the first input the user sees `state=idle` printed twice in
quick succession. Cosmetic but confusing while debugging.

### D-06 - `RobotRuntime` does not expose `ai_client` or `tts`

- `src/robotin/application/runtime.py:13-16,19-36`: `create_runtime` accepts
  `ai_client` and `tts` but `RobotRuntime` only stores `state_machine`,
  `display`, and `controller`.

A future task that needs to interact with the AI client outside the
controller (for example to inject conversational context, or to swap models
mid-session) will not be able to retrieve it from the runtime container.
Easy to fix now, harder to fix once callers exist.

### D-07 - `AIClient` contract does not document failure mode

- `src/robotin/interfaces/ai_client.py` declares `generate_response(text) -> str`
  with no exception contract.
- `HTTPAIClient` raises `HTTPAIClientError`, not caught by
  `RobotController.handle_text_turn`
  (`src/robotin/application/controller.py:28`).

It works only because `main.py` wraps the loop in a broad `except Exception`
and delegates to `recover_to_idle_after_error`. The contract should at
least document that implementations may raise, so future call sites do not
assume a total function.

---

## 3. Structural gaps (from Revision 01, still valid)

These are not defects but missing pieces from the planned architecture. Kept
here for completeness — see `Revision01.md` §9 for the full list.

| Gap                                          | Status                                       |
| -------------------------------------------- | -------------------------------------------- |
| `src/robotin/config.py`                      | Not created. Env access scattered.           |
| Logging strategy                             | Still `print()` everywhere.                  |
| STT interface and mock                       | Not defined.                                 |
| Event bus / event consumption                | Events defined but not wired to controller.  |
| `ResetRequestedEvent` recovery path          | Defined, never dispatched.                   |
| `assets/sounds/`, `assets/eyes/`             | Folders not created.                         |
| Configuration profiles (Windows / RPi)       | Single `.env` only.                          |
| Real adapters (Piper, openWakeWord, display) | In backlog.                                  |

---

## 4. Quality and process gaps

### Q-01 - No linter, formatter, or type checker

`pyproject.toml` defines only `pytest` as a dev dependency. With multiple
"agents" editing the codebase, a fixed style baseline (`ruff`, `black`,
optional `mypy --strict` for `domain/` and `application/`) prevents
formatting churn and catches typing regressions.

### Q-02 - No continuous integration

There is no CI workflow running `pytest` on push / PR. Easy to add (GitHub
Actions, ~20 lines) and prevents regressions when agents implement tasks.

### Q-03 - Test coverage holes

Existing tests are excellent in quality but leave a few gaps:

- No direct test of the `ERROR → IDLE` transition in
  `tests/test_state_machine.py` (only covered indirectly via
  `tests/test_runtime.py`).
- No test for invalid transitions originating from `LISTENING`, `PROCESSING`,
  or `SPEAKING` (`tests/test_state_machine.py:7-20` only checks invalid from
  `IDLE`).
- `tests/test_main.py` only covers the `exit` branch; the exception →
  recovery branch in `main.py:42-43` is untested.
- No test verifying that `HTTPAIClient` rejects non-http(s) URLs (depends on
  D-03 being fixed).

### Q-04 - `MockTTS` keeps state across runs

`src/robotin/infrastructure/tts_mock.py:5-9`: `spoken_texts` accumulates and
has no `reset()`. Today no test reuses the instance, but a fixture or a
`reset()` method would prevent surprises in future tests.

---

## 5. Errors in `Revision01.md` itself

Recorded so the next reviewer does not inherit the same blind spots:

- **§8 ("Strengths"):** *"Extensive documentation that stays consistent with
  the implementation"* — refuted by D-01.
- **§11 ("Summary"):** *"no apparent technical debt"* — refuted by D-01,
  D-02, D-03, D-04 and Q-01/Q-02.
- **§9 ("Gaps and improvement opportunities"):** lists only missing items.
  No defect in existing code is identified. The section reads as an
  inventory, not a code review.

---

## 6. Recommended task order

Defects first (low effort, removes hidden risks), then structural gaps from
Revision 01, then real adapters. Each item is sized to remain a small,
testable task per the project's `MASTER_PROMPT.md` working style.

### Phase A - Fix defects (small, safe, high value)

1. **Task 009 - Sync protocol documentation with `HTTPAIClient`** (D-01).
   Update `docs/protocol.md` to reflect actual request/response shapes; add
   a note that the document mirrors the code.
2. **Task 010 - Validate URL scheme in `HTTPAIClient`** (D-03).
   Reject anything other than `http` / `https` at construction time, with a
   test.
3. **Task 011 - Replace silent `pass` in error recovery** (D-04).
   Log the swallowed `ValueError` (after Q-05 logging strategy is in place;
   until then, surface it through `output_func`).
4. **Task 012 - Remove duplicate initial `show_state`** (D-05).
   Decide whether the controller or `main.py` is responsible for displaying
   the initial state, document the choice in `docs/architecture.md`.
5. **Task 013 - Document `AIClient` failure contract** (D-07).
   Add a docstring note on `interfaces/ai_client.py` and decide whether
   `RobotController` should translate `HTTPAIClientError` into a state
   transition or let it propagate.

### Phase B - Foundational structure (unblocks later tasks)

6. **Task 014 - `src/robotin/config.py` with `.env` loader** (Revision 01
   gap + D-02). Stdlib-only parser. Centralize all `os.getenv` calls,
   including `HTTPAIClient` defaults.
7. **Task 015 - Logging strategy** (Revision 01 gap). Replace `print()` in
   `main.py`, `runtime.py`, `display_mock.py`. Use `logging.getLogger("robotin")`.
   Keep `MockDisplay` deterministic for tests by injecting the logger.
8. **Task 016 - Expose `ai_client` and `tts` on `RobotRuntime`** (D-06).
   Tiny refactor; add to dataclass and update `create_runtime`.
9. **Task 017 - Test coverage for state transitions and error path** (Q-03).
   Add the missing transition tests and a test for the exception branch in
   `main.py`.
10. **Task 018 - Linter + formatter + CI** (Q-01, Q-02). `ruff` + `pytest`
    on push via GitHub Actions.

### Phase C - Voice abstraction completion

11. **Task 019 - STT interface + mock** (Revision 01 gap).
12. **Task 020 - Event bus minimal implementation** (Revision 01 gap).
    Wire `ResetRequestedEvent` to the recovery path so it is exercised by
    application logic, not only by `recover_to_idle_after_error`.

### Phase D - Real adapters (only after A, B, C)

13. **Task 021 - Piper TTS adapter** (backlog).
14. **Task 022 - openWakeWord adapter** (backlog).
15. **Task 023 - Raspberry Pi display adapter** (backlog).

---

## 7. Summary

The project's architectural discipline holds up under a second review. The
existing code is clean and the test suite passes (20/20). However, contrary
to Revision 01's closing line, there *is* technical debt — small, contained,
and easy to fix, but real. Most of it is one-line or one-file work that
should be cleared in Phase A before any new feature lands.

After Phase A and B, the project will be in the state Revision 01 already
described as "excellent": a solid foundation ready for real adapters with
no hidden inconsistencies between code, docs, and configuration.
