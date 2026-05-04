from robotin.domain.robot_state import RobotState
from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.infrastructure.display_mock import MockDisplay
from robotin.main import main, run_text_interaction_turn
from robotin.state_machine import StateMachine


def test_run_text_interaction_turn_moves_through_expected_states(
    capsys,
) -> None:
    state_machine = StateMachine()
    display = MockDisplay()
    ai_client = MockAIClient(responses={"hello": "Hi from mock."})
    outputs: list[str] = []

    response = run_text_interaction_turn(
        user_text="hello",
        state_machine=state_machine,
        display=display,
        ai_client=ai_client,
        output_func=outputs.append,
    )

    assert response == "Hi from mock."
    assert state_machine.current_state == RobotState.IDLE
    assert outputs == ["Robotin: Hi from mock."]

    captured = capsys.readouterr()
    assert "[MockDisplay] state=listening" in captured.out
    assert "[MockDisplay] state=processing" in captured.out
    assert "[MockDisplay] state=speaking" in captured.out
    assert "[MockDisplay] state=idle" in captured.out


def test_main_exits_when_user_types_exit() -> None:
    inputs = iter(["exit"])
    outputs: list[str] = []

    main(input_func=lambda _prompt: next(inputs), output_func=outputs.append)

    assert "Robotin started successfully." in outputs
    assert "Type a message and press Enter. Type 'exit' to quit." in outputs
    assert "Shutting down Robotin." in outputs

