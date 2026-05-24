from unittest.mock import MagicMock

from robotin.application.audio_turn import AudioTurnOrchestrator
from robotin.application.controller import RobotController
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.infrastructure.stt_mock import MockSpeechToText
from robotin.infrastructure.wake_word_mock import MockWakeWordDetector
from robotin.state_machine import StateMachine


def _build_controller() -> RobotController:
    return RobotController(
        state_machine=StateMachine(),
        display=MockDisplay(),
        ai_client=MockAIClient(responses={"hello": "hi from robotin"}),
    )


def test_audio_turn_returns_none_when_wake_word_is_not_detected() -> None:
    controller = MagicMock(spec=RobotController)
    orchestrator = AudioTurnOrchestrator(
        wake_word=MockWakeWordDetector(detections=[False]),
        stt=MockSpeechToText(transcripts=["hello"]),
        controller=controller,
    )

    assert orchestrator.run_once() is None
    controller.handle_text_turn.assert_not_called()


def test_audio_turn_returns_none_when_stt_has_no_transcript() -> None:
    controller = MagicMock(spec=RobotController)
    orchestrator = AudioTurnOrchestrator(
        wake_word=MockWakeWordDetector(detections=[True]),
        stt=MockSpeechToText(transcripts=[None]),
        controller=controller,
    )

    assert orchestrator.run_once() is None
    controller.handle_text_turn.assert_not_called()


def test_audio_turn_returns_none_when_transcript_is_blank() -> None:
    controller = MagicMock(spec=RobotController)
    orchestrator = AudioTurnOrchestrator(
        wake_word=MockWakeWordDetector(detections=[True]),
        stt=MockSpeechToText(transcripts=["   "]),
        controller=controller,
    )

    assert orchestrator.run_once() is None
    controller.handle_text_turn.assert_not_called()


def test_audio_turn_runs_controller_when_wake_word_and_transcript_exist() -> None:
    controller = _build_controller()
    orchestrator = AudioTurnOrchestrator(
        wake_word=MockWakeWordDetector(detections=[True]),
        stt=MockSpeechToText(transcripts=["hello"]),
        controller=controller,
    )

    assert orchestrator.run_once() == "hi from robotin"

