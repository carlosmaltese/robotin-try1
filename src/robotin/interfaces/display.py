from abc import ABC, abstractmethod

from robotin.domain.robot_state import RobotState


class Display(ABC):
    @abstractmethod
    def show_state(self, state: RobotState) -> None:
        """Render the current robot state."""
