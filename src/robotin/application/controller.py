from robotin.domain.robot_state import RobotState
from robotin.interfaces.ai_client import AIClient
from robotin.interfaces.display import Display
from robotin.state_machine import StateMachine


class RobotController:
    def __init__(
        self,
        state_machine: StateMachine,
        display: Display,
        ai_client: AIClient,
    ) -> None:
        self._state_machine = state_machine
        self._display = display
        self._ai_client = ai_client

    def handle_text_turn(self, user_text: str) -> str:
        self._state_machine.transition_to(RobotState.LISTENING)
        self._display.show_state(self._state_machine.current_state)

        self._state_machine.transition_to(RobotState.PROCESSING)
        self._display.show_state(self._state_machine.current_state)

        response = self._ai_client.generate_response(user_text)

        self._state_machine.transition_to(RobotState.SPEAKING)
        self._display.show_state(self._state_machine.current_state)

        self._state_machine.transition_to(RobotState.IDLE)
        self._display.show_state(self._state_machine.current_state)
        return response

