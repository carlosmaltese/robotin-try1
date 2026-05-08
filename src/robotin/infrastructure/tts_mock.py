from robotin.interfaces.tts import TTS


class MockTTS(TTS):
    def __init__(self) -> None:
        self.spoken_texts: list[str] = []

    def speak(self, text: str) -> None:
        self.spoken_texts.append(text)
