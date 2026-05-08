from abc import ABC, abstractmethod


class TTS(ABC):
    @abstractmethod
    def speak(self, text: str) -> None:
        """Render speech output for the given text."""
