from unittest.mock import MagicMock, patch

from robotin.infrastructure.ai_client_mock import MockAIClient
from robotin.main import main


def test_main_exits_when_user_types_exit() -> None:
    inputs = iter(["exit"])
    outputs: list[str] = []

    main(input_func=lambda _prompt: next(inputs), output_func=outputs.append)

    assert "Robotin started successfully." in outputs
    assert "Type a message and press Enter. Type 'exit' to quit." in outputs
    assert "Shutting down Robotin." in outputs


def test_main_recovers_and_continues_after_ai_error() -> None:
    call_count = 0

    def failing_then_exit(_prompt: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "hello"
        return "exit"

    outputs: list[str] = []

    failing_client = MagicMock(spec=MockAIClient)
    failing_client.generate_response.side_effect = RuntimeError("AI down")

    with patch("robotin.application.runtime.MockAIClient", return_value=failing_client):
        main(input_func=failing_then_exit, output_func=outputs.append)

    assert any("Robotin error:" in line for line in outputs)
    assert "Shutting down Robotin." in outputs
