from robotin.domain.robot_state import RobotState
from robotin.interfaces.display import Display


class MockDisplay(Display):
    def show_state(self, state: RobotState) -> None:
        print(f"[MockDisplay] state={state.value}")
