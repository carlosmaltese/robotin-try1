from abc import ABC, abstractmethod


class WakeWordDetector(ABC):
    @abstractmethod
    def detect_once(self) -> bool:
        """Return True when wake word is detected for a single check."""
