from robotin.infrastructure.display_mock import MockDisplay
from robotin.state_machine import StateMachine


def main() -> None:
    display = MockDisplay()
    state_machine = StateMachine()
    display.show_state(state_machine.current_state)
    print("Robotin started successfully.")


if __name__ == "__main__":
    main()
