import logging
from collections.abc import Callable

from robotin.application.runtime import create_runtime, recover_to_idle_after_error
from robotin.config import load_config
from robotin.infrastructure.display_mock import MockDisplay
from robotin.state_machine import StateMachine


def main(
    input_func: Callable[[str], str] = input,
    output_func: Callable[[str], None] = print,
) -> None:
    config = load_config()
    logging.basicConfig(level=config.log_level)
    display = MockDisplay()
    state_machine = StateMachine()

    runtime = create_runtime(
        state_machine=state_machine,
        display=display,
        config=config,
    )

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

            response = runtime.controller.handle_text_turn(user_text)
            output_func(f"Robotin: {response}")
        except (KeyboardInterrupt, EOFError):
            output_func("\nShutting down Robotin.")
            return
        except Exception as exc:
            recover_to_idle_after_error(runtime, output_func, exc)


if __name__ == "__main__":
    main()
