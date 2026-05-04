from robotin.events import (
    AIResponseReceivedEvent,
    ActivationRequestedEvent,
    ErrorOccurredEvent,
    EventType,
    ResetRequestedEvent,
    SpeechFinishedEvent,
    TextReceivedEvent,
)


def test_event_types_and_payloads() -> None:
    activation_event = ActivationRequestedEvent()
    text_event = TextReceivedEvent(text="hello")
    ai_response_event = AIResponseReceivedEvent(response_text="hi there")
    speech_finished_event = SpeechFinishedEvent()
    error_event = ErrorOccurredEvent(message="something went wrong")
    reset_event = ResetRequestedEvent()

    assert activation_event.type == EventType.ACTIVATION_REQUESTED
    assert text_event.type == EventType.TEXT_RECEIVED
    assert text_event.text == "hello"
    assert ai_response_event.type == EventType.AI_RESPONSE_RECEIVED
    assert ai_response_event.response_text == "hi there"
    assert speech_finished_event.type == EventType.SPEECH_FINISHED
    assert error_event.type == EventType.ERROR_OCCURRED
    assert error_event.message == "something went wrong"
    assert reset_event.type == EventType.RESET_REQUESTED
