import logging
from unittest.mock import MagicMock

from robotin.application.runtime import RobotRuntime, create_runtime, recover_to_idle_after_error
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.infrastructure.tts_mock import MockTTS
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
    assert runtime.ai_client is ai_client
    assert runtime.tts is None


def test_recover_to_idle_logs_warning_when_transition_to_error_fails(caplog) -> None:
    mock_sm = MagicMock()
    mock_sm.current_state = RobotState.IDLE
    mock_sm.transition_to.side_effect = ValueError("forced failure")

    display = MockDisplay()
    ai_client = MockAIClient()
    controller = MagicMock()

    runtime = RobotRuntime(
        state_machine=mock_sm,
        display=display,
        controller=controller,
        ai_client=ai_client,
        tts=None,
    )

    outputs: list[str] = []
    with caplog.at_level(logging.WARNING, logger="robotin"):
        recover_to_idle_after_error(runtime, outputs.append, RuntimeError("oops"))

    assert "Could not transition to ERROR" in caplog.text


def test_create_runtime_exposes_tts_when_provided() -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()
    tts = MockTTS()

    runtime = create_runtime(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
        tts=tts,
    )

    assert runtime.tts is tts


def test_recover_to_idle_after_error_transitions_safely(caplog) -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()
    runtime = create_runtime(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )
    outputs: list[str] = []

    with caplog.at_level(logging.INFO, logger="robotin"):
        recover_to_idle_after_error(runtime, outputs.append, RuntimeError("boom"))

    assert "state=error" in caplog.text
    assert "state=idle" in caplog.text
    assert outputs == ["Robotin error: boom"]
    assert runtime.state_machine.current_state.value == "idle"
