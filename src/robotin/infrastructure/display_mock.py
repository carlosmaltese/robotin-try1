import logging

from robotin.domain.robot_state import RobotState
from robotin.interfaces.display import Display

_logger = logging.getLogger("robotin")


class MockDisplay(Display):
    def show_state(self, state: RobotState) -> None:
        _logger.info("[MockDisplay] state=%s", state.value)
