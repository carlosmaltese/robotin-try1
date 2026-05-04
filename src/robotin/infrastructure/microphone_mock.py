from robotin.interfaces.microphone import Microphone


class MockMicrophone(Microphone):
    def __init__(self, inputs: list[str | None] | None = None) -> None:
        self._inputs = list(inputs or [])

    def listen_once(self) -> str | None:
        if not self._inputs:
            return None
        return self._inputs.pop(0)

