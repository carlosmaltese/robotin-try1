from robotin.interfaces.wake_word import WakeWordDetector


class MockWakeWordDetector(WakeWordDetector):
    def __init__(self, detections: list[bool] | None = None) -> None:
        self._detections = list(detections or [])

    def detect_once(self) -> bool:
        if not self._detections:
            return False
        return self._detections.pop(0)
