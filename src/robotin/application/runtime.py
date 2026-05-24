import logging
from collections.abc import Callable
from dataclasses import dataclass

from robotin.application.controller import RobotController
from robotin.config import AI_MODE_HTTP, AI_MODE_MOCK, RobotinConfig, STT_MODE_MOCK, STT_MODE_REMOTE
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_http import HTTPAIClient
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.stt_mock import MockSpeechToText
from robotin.infrastructure.stt_remote import RemoteSpeechToText
from robotin.infrastructure.wake_word_mock import MockWakeWordDetector
from robotin.interfaces.ai_client import AIClient
from robotin.interfaces.display import Display
from robotin.interfaces.stt import SpeechToText
from robotin.interfaces.tts import TTS
from robotin.interfaces.wake_word import WakeWordDetector
from robotin.state_machine import StateMachine

_logger = logging.getLogger("robotin")


@dataclass(frozen=True)
class RobotRuntime:
    state_machine: StateMachine
    display: Display
    controller: RobotController
    ai_client: AIClient
    wake_word: WakeWordDetector
    stt: SpeechToText
    tts: TTS | None


def create_runtime(
    *,
    state_machine: StateMachine,
    display: Display,
    config: RobotinConfig,
    ai_client: AIClient | None = None,
    wake_word: WakeWordDetector | None = None,
    stt: SpeechToText | None = None,
    tts: TTS | None = None,
) -> RobotRuntime:
    if ai_client is None:
        if config.ai_mode == AI_MODE_MOCK:
            ai_client = MockAIClient()
        elif config.ai_mode == AI_MODE_HTTP:
            ai_client = HTTPAIClient(config=config)
        else:
            raise ValueError(f"Unsupported AI mode: {config.ai_mode}")

    if stt is None:
        if config.stt_mode == STT_MODE_MOCK:
            stt = MockSpeechToText()
        elif config.stt_mode == STT_MODE_REMOTE:
            stt = RemoteSpeechToText(config=config)
        else:
            raise ValueError(f"Unsupported STT mode: {config.stt_mode}")

    if wake_word is None:
        wake_word = MockWakeWordDetector()

    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
        tts=tts,
    )
    return RobotRuntime(
        state_machine=state_machine,
        display=display,
        controller=controller,
        ai_client=ai_client,
        wake_word=wake_word,
        stt=stt,
        tts=tts,
    )


def recover_to_idle_after_error(
    runtime: RobotRuntime,
    output_func: Callable[[str], None],
    exc: Exception,
) -> None:
    _logger.error("Error during operation", exc_info=True)
    if runtime.state_machine.current_state != RobotState.ERROR:
        try:
            runtime.state_machine.transition_to(RobotState.ERROR)
        except ValueError:
            _logger.warning(
                "Could not transition to ERROR from %s; already in safe state.",
                runtime.state_machine.current_state.value,
            )

    runtime.display.show_state(runtime.state_machine.current_state)
    output_func(f"Robotin error: {exc}")

    if runtime.state_machine.current_state == RobotState.ERROR:
        runtime.state_machine.transition_to(RobotState.IDLE)
        runtime.display.show_state(runtime.state_machine.current_state)
