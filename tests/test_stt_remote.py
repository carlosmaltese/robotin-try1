import pytest

from robotin.config import RobotinConfig
from robotin.infrastructure.stt_remote import RemoteSpeechToText


def test_remote_stt_accepts_valid_config() -> None:
    config = RobotinConfig(
        stt_mode="remote",
        stt_base_url="http://127.0.0.1:8010",
        stt_timeout_seconds=2.5,
    )

    stt = RemoteSpeechToText(config=config)

    assert stt is not None


def test_remote_stt_rejects_invalid_base_url_scheme() -> None:
    with pytest.raises(ValueError, match="http or https"):
        RemoteSpeechToText(base_url="file:///tmp/stt", timeout_seconds=1.0)


def test_remote_stt_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        RemoteSpeechToText(base_url="http://127.0.0.1:8010", timeout_seconds=0)


def test_remote_stt_stub_is_explicitly_unimplemented() -> None:
    stt = RemoteSpeechToText(base_url="http://127.0.0.1:8010", timeout_seconds=1.0)

    with pytest.raises(NotImplementedError, match="not implemented yet"):
        stt.transcribe_once()

