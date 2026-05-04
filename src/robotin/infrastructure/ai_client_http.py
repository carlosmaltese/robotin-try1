import json
import os
from urllib import error, request

from robotin.interfaces.ai_client import AIClient


class HTTPAIClientError(RuntimeError):
    """Raised when the local HTTP AI client cannot return a valid response."""


class HTTPAIClient(AIClient):
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._base_url = (base_url or os.getenv("ROBOTIN_AI_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
        self._timeout_seconds = timeout_seconds if timeout_seconds is not None else float(
            os.getenv("ROBOTIN_AI_TIMEOUT_SECONDS", "3.0")
        )

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
        except error.URLError as exc:
            raise HTTPAIClientError(f"Local AI request failed: {exc}") from exc
        except TimeoutError as exc:
            raise HTTPAIClientError("Local AI request timed out") from exc

        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise HTTPAIClientError("Local AI response was not valid JSON") from exc

        reply = data.get("response")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPAIClientError("Local AI response payload is missing 'response' text")

        return reply

