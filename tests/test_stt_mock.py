from robotin.infrastructure.stt_mock import MockSpeechToText


def test_mock_stt_returns_transcripts_in_order_then_none() -> None:
    stt = MockSpeechToText(transcripts=["hello robotin", None, "tell me a story"])

    assert stt.transcribe_once() == "hello robotin"
    assert stt.transcribe_once() is None
    assert stt.transcribe_once() == "tell me a story"
    assert stt.transcribe_once() is None


def test_mock_stt_returns_none_without_predefined_transcripts() -> None:
    stt = MockSpeechToText()

    assert stt.transcribe_once() is None
