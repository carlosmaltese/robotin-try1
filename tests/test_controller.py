import logging

import pytest

from robotin.application.controller import RobotController
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.infrastructure.tts_mock import MockTTS
from robotin.interfaces.ai_client import AIClient
from robotin.state_machine import StateMachine


def test_handle_text_turn_moves_through_expected_states(caplog) -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient(responses={"hello": "Hi from mock."})
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    with caplog.at_level(logging.INFO, logger="robotin"):
        response = controller.handle_text_turn("hello")

    assert response == "Hi from mock."
    assert state_machine.current_state == RobotState.IDLE
    assert "state=listening" in caplog.text
    assert "state=processing" in caplog.text
    assert "state=speaking" in caplog.text
    assert "state=idle" in caplog.text


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


def test_handle_text_turn_propagates_ai_client_exception() -> None:
    class FailingAIClient(AIClient):
        def generate_response(self, text: str) -> str:
            raise RuntimeError("AI unavailable")

    state_machine = StateMachine()
    display = MockDisplay()
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=FailingAIClient(),
    )

    with pytest.raises(RuntimeError, match="AI unavailable"):
        controller.handle_text_turn("hello")


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
