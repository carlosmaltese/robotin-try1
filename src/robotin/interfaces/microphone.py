from abc import ABC, abstractmethod


class Microphone(ABC):
    @abstractmethod
    def listen_once(self) -> str | None:
        """Return one captured text sample, or None when no speech is available."""
