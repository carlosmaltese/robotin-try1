import logging
from collections.abc import Callable
from dataclasses import dataclass

from robotin.application.controller import RobotController
from robotin.domain.robot_state import RobotState
from robotin.interfaces.ai_client import AIClient
from robotin.interfaces.display import Display
from robotin.interfaces.tts import TTS
from robotin.state_machine import StateMachine

_logger = logging.getLogger("robotin")


@dataclass(frozen=True)
class RobotRuntime:
    state_machine: StateMachine
    display: Display
    controller: RobotController
    ai_client: AIClient
    tts: TTS | None


def create_runtime(
    *,
    state_machine: StateMachine,
    display: Display,
    ai_client: AIClient,
    tts: TTS | None = None,
) -> RobotRuntime:
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
