from robotin.infrastructure.ai_client_mock import MockAIClient


def test_mock_ai_client_returns_predefined_response() -> None:
    client = MockAIClient(responses={"hello": "Hi! Nice to meet you."})

    assert client.generate_response("hello") == "Hi! Nice to meet you."


def test_mock_ai_client_returns_deterministic_fallback_response() -> None:
    client = MockAIClient()

    assert client.generate_response("How are you?") == "I heard you say: How are you?."


def test_mock_ai_client_handles_empty_input() -> None:
    client = MockAIClient()

    assert client.generate_response("   ") == "Please say something so I can help you."
