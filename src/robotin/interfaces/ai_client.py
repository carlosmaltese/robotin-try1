from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    def generate_response(self, text: str) -> str:
        """Return a text response for the given input."""
