from robotin.interfaces.ai_client import AIClient


class MockAIClient(AIClient):
    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self._responses = dict(responses or {})

    def generate_response(self, text: str) -> str:
        normalized_text = text.strip()
        if not normalized_text:
            return "Please say something so I can help you."
        if normalized_text in self._responses:
            return self._responses[normalized_text]
        return f"I heard you say: {normalized_text}."
