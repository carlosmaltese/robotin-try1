from robotin.main import main


def test_main_exits_when_user_types_exit() -> None:
    inputs = iter(["exit"])
    outputs: list[str] = []

    main(input_func=lambda _prompt: next(inputs), output_func=outputs.append)

    assert "Robotin started successfully." in outputs
    assert "Type a message and press Enter. Type 'exit' to quit." in outputs
    assert "Shutting down Robotin." in outputs

