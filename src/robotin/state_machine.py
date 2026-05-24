from robotin.domain.robot_state import RobotState


class StateMachine:
    _ALLOWED_TRANSITIONS = {
        RobotState.IDLE: {RobotState.LISTENING, RobotState.ERROR},
        RobotState.LISTENING: {RobotState.PROCESSING, RobotState.ERROR},
        RobotState.PROCESSING: {RobotState.SPEAKING, RobotState.ERROR},
        RobotState.SPEAKING: {RobotState.IDLE, RobotState.ERROR},
        RobotState.ERROR: {RobotState.IDLE},
    }

    def __init__(self) -> None:
        self._state = RobotState.IDLE

    @property
    def current_state(self) -> RobotState:
        return self._state

    def transition_to(self, next_state: RobotState) -> None:
        allowed = self._ALLOWED_TRANSITIONS[self._state]
        if next_state not in allowed:
            raise ValueError(f"Invalid transition from {self._state.value} to {next_state.value}")
        self._state = next_state
