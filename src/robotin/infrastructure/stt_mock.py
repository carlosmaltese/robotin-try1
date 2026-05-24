from robotin.interfaces.stt import SpeechToText


class MockSpeechToText(SpeechToText):
    def __init__(self, transcripts: list[str | None] | None = None) -> None:
        self._transcripts = list(transcripts or [])

    def transcribe_once(self) -> str | None:
        if not self._transcripts:
            return None
        return self._transcripts.pop(0)
