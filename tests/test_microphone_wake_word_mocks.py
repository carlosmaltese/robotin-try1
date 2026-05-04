from robotin.infrastructure.microphone_mock import MockMicrophone
from robotin.infrastructure.wake_word_mock import MockWakeWordDetector


def test_mock_microphone_returns_inputs_in_order_then_none() -> None:
    mic = MockMicrophone(inputs=["hello", None, "robotin"])

    assert mic.listen_once() == "hello"
    assert mic.listen_once() is None
    assert mic.listen_once() == "robotin"
    assert mic.listen_once() is None


def test_mock_wake_word_returns_detections_in_order_then_false() -> None:
    detector = MockWakeWordDetector(detections=[False, True])

    assert detector.detect_once() is False
    assert detector.detect_once() is True
    assert detector.detect_once() is False

