from collections.abc import Callable

from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.interfaces.ai_client import AIClient
from robotin.interfaces.display import Display
from robotin.state_machine import StateMachine


def run_text_interaction_turn(
    user_text: str,
    state_machine: StateMachine,
    display: Display,
    ai_client: AIClient,
    output_func: Callable[[str], None],
) -> str:
    state_machine.transition_to(RobotState.LISTENING)
    display.show_state(state_machine.current_state)

    state_machine.transition_to(RobotState.PROCESSING)
    display.show_state(state_machine.current_state)

    response = ai_client.generate_response(user_text)

    state_machine.transition_to(RobotState.SPEAKING)
    display.show_state(state_machine.current_state)
    output_func(f"Robotin: {response}")

    state_machine.transition_to(RobotState.IDLE)
    display.show_state(state_machine.current_state)
    return response


def main(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    display = MockDisplay()
    ai_client = MockAIClient()
    state_machine = StateMachine()

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

            run_text_interaction_turn(
                user_text=user_text,
                state_machine=state_machine,
                display=display,
                ai_client=ai_client,
                output_func=output_func,
            )
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
