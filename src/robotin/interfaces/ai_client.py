from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    def generate_response(self, text: str) -> str:
        """Return a text response for the given input.

        Implementations may raise. The only documented exception type today is
        HTTPAIClientError. Callers must not assume this method is total.
        """
