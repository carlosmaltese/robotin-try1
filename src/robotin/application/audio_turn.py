from robotin.application.controller import RobotController
from robotin.interfaces.stt import SpeechToText
from robotin.interfaces.wake_word import WakeWordDetector


class AudioTurnOrchestrator:
    """Coordinate one wake-word-driven audio turn.

    This orchestrator keeps audio loop policy inside application code while
    delegating all concrete audio/STT behavior to injected interfaces.
    """

    def __init__(
        self,
        *,
        wake_word: WakeWordDetector,
        stt: SpeechToText,
        controller: RobotController,
    ) -> None:
        self._wake_word = wake_word
        self._stt = stt
        self._controller = controller

    def run_once(self) -> str | None:
        """Run one non-blocking audio cycle.

        Returns:
            - assistant response text when a full turn was completed,
            - None when wake word is absent or no usable transcript exists.
        """

        if not self._wake_word.detect_once():
            return None

        transcript = self._stt.transcribe_once()
        if transcript is None:
            return None

        user_text = transcript.strip()
        if not user_text:
            return None

        return self._controller.handle_text_turn(user_text)
