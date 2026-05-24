import json
import os
from urllib import error, request
from urllib.parse import urlsplit

from robotin.config import RobotinConfig
from robotin.interfaces.ai_client import AIClient


class HTTPAIClientError(RuntimeError):
    """Raised when the local HTTP AI client cannot return a valid response."""


class HTTPAIClient(AIClient):
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        config: RobotinConfig | None = None,
    ) -> None:
        _config_url = config.ai_base_url if config is not None else None
        _config_timeout = config.ai_timeout_seconds if config is not None else None

        if base_url is not None:
            resolved_url = base_url
        elif _config_url is not None:
            resolved_url = _config_url
        else:
            resolved_url = os.getenv("ROBOTIN_AI_BASE_URL") or "http://127.0.0.1:8000"
        self._base_url = resolved_url.rstrip("/")
        if timeout_seconds is not None:
            self._timeout_seconds = timeout_seconds
        elif _config_timeout is not None:
            self._timeout_seconds = _config_timeout
        else:
            self._timeout_seconds = float(os.getenv("ROBOTIN_AI_TIMEOUT_SECONDS", "3.0"))

        parsed = urlsplit(self._base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(f"base_url must use http or https scheme, got: {self._base_url!r}")

        if self._timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

    def generate_response(self, text: str) -> str:
        payload = {"text": text}
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url=f"{self._base_url}/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self._timeout_seconds) as response:
                status_code = getattr(response, "status", response.getcode())
                if status_code != 200:
                    raise HTTPAIClientError(f"Local AI server returned status {status_code}")

                raw_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise HTTPAIClientError(f"Local AI server returned status {exc.code}") from exc
        except TimeoutError as exc:
            raise HTTPAIClientError("Local AI request timed out") from exc
        except error.URLError as exc:
            raise HTTPAIClientError(f"Local AI request failed: {exc}") from exc

        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise HTTPAIClientError("Local AI response was not valid JSON") from exc

        reply = data.get("response")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPAIClientError("Local AI response payload is missing 'response' text")

        return reply
