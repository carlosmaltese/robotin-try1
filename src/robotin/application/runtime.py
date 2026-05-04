from collections.abc import Callable
from dataclasses import dataclass

from robotin.application.controller import RobotController
from robotin.domain.robot_state import RobotState
from robotin.interfaces.ai_client import AIClient
from robotin.interfaces.display import Display
from robotin.interfaces.tts import TTS
from robotin.state_machine import StateMachine


@dataclass(frozen=True)
class RobotRuntime:
    state_machine: StateMachine
    display: Display
    controller: RobotController


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
    )


def recover_to_idle_after_error(
    runtime: RobotRuntime,
    output_func: Callable[[str], None],
    exc: Exception,
) -> None:
    if runtime.state_machine.current_state != RobotState.ERROR:
        try:
            runtime.state_machine.transition_to(RobotState.ERROR)
        except ValueError:
            pass

    runtime.display.show_state(runtime.state_machine.current_state)
    output_func(f"Robotin error: {exc}")

    if runtime.state_machine.current_state == RobotState.ERROR:
        runtime.state_machine.transition_to(RobotState.IDLE)
        runtime.display.show_state(runtime.state_machine.current_state)

