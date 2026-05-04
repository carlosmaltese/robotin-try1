from robotin.application.controller import RobotController
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.infrastructure.tts_mock import MockTTS
from robotin.state_machine import StateMachine


def test_handle_text_turn_moves_through_expected_states(capsys) -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient(responses={"hello": "Hi from mock."})
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    response = controller.handle_text_turn("hello")

    assert response == "Hi from mock."
    assert state_machine.current_state == RobotState.IDLE

    captured = capsys.readouterr()
    assert "[MockDisplay] state=listening" in captured.out
    assert "[MockDisplay] state=processing" in captured.out
    assert "[MockDisplay] state=speaking" in captured.out
    assert "[MockDisplay] state=idle" in captured.out


def test_handle_text_turn_uses_deterministic_mock_fallback() -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    response = controller.handle_text_turn("How are you?")

    assert response == "I heard you say: How are you?."
    assert state_machine.current_state == RobotState.IDLE


def test_handle_text_turn_calls_tts_when_injected() -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient(responses={"hello": "Hi from mock."})
    tts = MockTTS()
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
        tts=tts,
    )

    response = controller.handle_text_turn("hello")

    assert response == "Hi from mock."
    assert tts.spoken_texts == ["Hi from mock."]
    assert state_machine.current_state == RobotState.IDLE

