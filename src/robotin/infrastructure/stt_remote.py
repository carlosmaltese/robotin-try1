from urllib.parse import urlsplit

from robotin.config import RobotinConfig
from robotin.interfaces.stt import SpeechToText


class RemoteSpeechToText(SpeechToText):
    """First real-ready STT adapter stub.

    This class validates network-facing configuration and intentionally keeps
    `transcribe_once()` unimplemented for now.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        config: RobotinConfig | None = None,
    ) -> None:
        config_url = config.stt_base_url if config is not None else None
        config_timeout = config.stt_timeout_seconds if config is not None else None

        resolved_url = base_url if base_url is not None else (config_url or "http://127.0.0.1:8010")
        self._base_url = resolved_url.rstrip("/")

        resolved_timeout = timeout_seconds if timeout_seconds is not None else (config_timeout or 3.0)
        self._timeout_seconds = resolved_timeout

        parsed = urlsplit(self._base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"stt base_url must use http or https scheme, got: {self._base_url!r}")

        if self._timeout_seconds <= 0:
            raise ValueError("stt timeout_seconds must be greater than 0")

    def transcribe_once(self) -> str | None:
        raise NotImplementedError("RemoteSpeechToText transcribe_once() is not implemented yet")

