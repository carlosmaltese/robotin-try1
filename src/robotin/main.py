from collections.abc import Callable

from robotin.application.controller import RobotController
from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.state_machine import StateMachine


def main(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    display = MockDisplay()
    ai_client = MockAIClient()
    state_machine = StateMachine()
    controller = RobotController(
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
    )

    display.show_state(state_machine.current_state)
    output_func("Robotin started successfully.")
    output_func("Type a message and press Enter. Type 'exit' to quit.")

    while True:
        try:
            user_text = input_func("You: ").strip()
            if user_text.lower() == "exit":
                output_func("Shutting down Robotin.")
                return
            if not user_text:
                output_func("Please type a message or 'exit'.")
                continue

            response = controller.handle_text_turn(user_text)
            output_func(f"Robotin: {response}")
        except (KeyboardInterrupt, EOFError):
            output_func("\nShutting down Robotin.")
            return
        except Exception as exc:
            if state_machine.current_state != RobotState.ERROR:
                try:
                    state_machine.transition_to(RobotState.ERROR)
                except ValueError:
                    pass
            display.show_state(state_machine.current_state)
            output_func(f"Robotin error: {exc}")
            if state_machine.current_state == RobotState.ERROR:
                state_machine.transition_to(RobotState.IDLE)
                display.show_state(state_machine.current_state)


if __name__ == "__main__":
    main()
