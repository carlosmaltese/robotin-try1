from abc import ABC, abstractmethod


class SpeechToText(ABC):
    @abstractmethod
    def transcribe_once(self) -> str | None:
        """Return one transcript, or None when no transcript is available."""
