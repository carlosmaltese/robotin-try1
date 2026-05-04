from robotin.application.runtime import create_runtime, recover_to_idle_after_error
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.state_machine import StateMachine


def test_create_runtime_wires_dependencies() -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()

    runtime = create_runtime(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    assert runtime.state_machine is state_machine
    assert runtime.display is display


def test_recover_to_idle_after_error_transitions_safely(capsys) -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()
    runtime = create_runtime(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )
    outputs: list[str] = []

    recover_to_idle_after_error(runtime, outputs.append, RuntimeError("boom"))

    captured = capsys.readouterr()
    assert "[MockDisplay] state=error" in captured.out
    assert "[MockDisplay] state=idle" in captured.out
    assert outputs == ["Robotin error: boom"]
    assert runtime.state_machine.current_state.value == "idle"

