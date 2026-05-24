import logging
from unittest.mock import MagicMock

from robotin.application.runtime import RobotRuntime, create_runtime, recover_to_idle_after_error
from robotin.config import RobotinConfig
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_http import HTTPAIClient
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.infrastructure.stt_mock import MockSpeechToText
from robotin.infrastructure.stt_remote import RemoteSpeechToText
from robotin.infrastructure.tts_mock import MockTTS
from robotin.infrastructure.wake_word_mock import MockWakeWordDetector
from robotin.state_machine import StateMachine


def test_create_runtime_wires_dependencies() -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient()

    runtime = create_runtime(
        config=RobotinConfig(),
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    assert runtime.state_machine is state_machine
    assert runtime.display is display
    assert runtime.ai_client is ai_client
    assert isinstance(runtime.wake_word, MockWakeWordDetector)
    assert isinstance(runtime.stt, MockSpeechToText)
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
        wake_word=MockWakeWordDetector(),
        stt=MockSpeechToText(),
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
        config=RobotinConfig(),
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
        config=RobotinConfig(),
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


def test_create_runtime_selects_mock_ai_client_when_mode_is_mock() -> None:
    runtime = create_runtime(
        config=RobotinConfig(ai_mode="mock"),
        state_machine=StateMachine(),
        display=MockDisplay(),
    )

    assert isinstance(runtime.ai_client, MockAIClient)


def test_create_runtime_selects_http_ai_client_when_mode_is_http() -> None:
    runtime = create_runtime(
        config=RobotinConfig(
            ai_mode="http",
            ai_base_url="http://127.0.0.1:11434",
            ai_timeout_seconds=2.0,
        ),
        state_machine=StateMachine(),
        display=MockDisplay(),
    )

    assert isinstance(runtime.ai_client, HTTPAIClient)


def test_create_runtime_selects_mock_stt_when_mode_is_mock() -> None:
    runtime = create_runtime(
        config=RobotinConfig(stt_mode="mock"),
        state_machine=StateMachine(),
        display=MockDisplay(),
    )

    assert isinstance(runtime.stt, MockSpeechToText)


def test_create_runtime_selects_remote_stt_when_mode_is_remote() -> None:
    runtime = create_runtime(
        config=RobotinConfig(
            stt_mode="remote",
            stt_base_url="http://127.0.0.1:8010",
            stt_timeout_seconds=2.0,
        ),
        state_machine=StateMachine(),
        display=MockDisplay(),
    )

    assert isinstance(runtime.stt, RemoteSpeechToText)


def test_create_runtime_uses_injected_wake_word() -> None:
    wake_word = MockWakeWordDetector(detections=[True])
    runtime = create_runtime(
        config=RobotinConfig(),
        state_machine=StateMachine(),
        display=MockDisplay(),
        wake_word=wake_word,
    )

    assert runtime.wake_word is wake_word
