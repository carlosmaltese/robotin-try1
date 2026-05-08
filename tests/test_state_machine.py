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


def test_state_machine_error_to_idle() -> None:
    sm = StateMachine()
    sm.transition_to(RobotState.ERROR)
    sm.transition_to(RobotState.IDLE)
    assert sm.current_state == RobotState.IDLE


def test_state_machine_invalid_transition_from_listening() -> None:
    sm = StateMachine()
    sm.transition_to(RobotState.LISTENING)
    with pytest.raises(ValueError):
        sm.transition_to(RobotState.SPEAKING)


def test_state_machine_invalid_transition_from_processing() -> None:
    sm = StateMachine()
    sm.transition_to(RobotState.LISTENING)
    sm.transition_to(RobotState.PROCESSING)
    with pytest.raises(ValueError):
        sm.transition_to(RobotState.IDLE)


def test_state_machine_invalid_transition_from_speaking() -> None:
    sm = StateMachine()
    sm.transition_to(RobotState.LISTENING)
    sm.transition_to(RobotState.PROCESSING)
    sm.transition_to(RobotState.SPEAKING)
    with pytest.raises(ValueError):
        sm.transition_to(RobotState.PROCESSING)
