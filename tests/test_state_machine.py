import pytest

from robotin.domain.robot_state import RobotState
from robotin.state_machine import StateMachine


def test_state_machine_valid_flow_and_invalid_transition() -> None:
    state_machine = StateMachine()

    assert state_machine.current_state == RobotState.IDLE

    state_machine.transition_to(RobotState.LISTENING)
    state_machine.transition_to(RobotState.PROCESSING)
    state_machine.transition_to(RobotState.SPEAKING)
    state_machine.transition_to(RobotState.IDLE)

    assert state_machine.current_state == RobotState.IDLE

    with pytest.raises(ValueError):
        state_machine.transition_to(RobotState.SPEAKING)
