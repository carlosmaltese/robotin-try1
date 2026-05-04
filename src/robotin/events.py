from dataclasses import dataclass
from enum import Enum


class EventType(str, Enum):
    ACTIVATION_REQUESTED = "activation_requested"
    TEXT_RECEIVED = "text_received"
    AI_RESPONSE_RECEIVED = "ai_response_received"
    SPEECH_FINISHED = "speech_finished"
    ERROR_OCCURRED = "error_occurred"
    RESET_REQUESTED = "reset_requested"


@dataclass(frozen=True)
class ActivationRequestedEvent:
    type: EventType = EventType.ACTIVATION_REQUESTED


@dataclass(frozen=True)
class TextReceivedEvent:
    text: str
    type: EventType = EventType.TEXT_RECEIVED


@dataclass(frozen=True)
class AIResponseReceivedEvent:
    response_text: str
    type: EventType = EventType.AI_RESPONSE_RECEIVED


@dataclass(frozen=True)
class SpeechFinishedEvent:
    type: EventType = EventType.SPEECH_FINISHED


@dataclass(frozen=True)
class ErrorOccurredEvent:
    message: str
    type: EventType = EventType.ERROR_OCCURRED


@dataclass(frozen=True)
class ResetRequestedEvent:
    type: EventType = EventType.RESET_REQUESTED
