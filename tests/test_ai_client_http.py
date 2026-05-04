import json
import socket
from unittest.mock import patch
from urllib import error

import pytest

from robotin.infrastructure.ai_client_http import HTTPAIClient, HTTPAIClientError


class _FakeHTTPResponse:
    def __init__(self, body: str, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> "_FakeHTTPResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_http_ai_client_returns_response_from_local_server() -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(http_request, timeout: float):
        captured["url"] = http_request.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(http_request.data.decode("utf-8"))
        return _FakeHTTPResponse('{"response": "hello from local server"}', status=200)

    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.5)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        response = client.generate_response("hi")

    assert response == "hello from local server"
    assert captured["url"] == "http://127.0.0.1:11434/generate"
    assert captured["timeout"] == 1.5
    assert captured["payload"] == {"text": "hi"}


def test_http_ai_client_raises_on_connection_error() -> None:
    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.0)

    with patch("urllib.request.urlopen", side_effect=error.URLError("connection refused")):
        with pytest.raises(HTTPAIClientError, match="Local AI request failed"):
            client.generate_response("hello")


def test_http_ai_client_raises_on_http_error_status() -> None:
    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.0)

    with patch(
        "urllib.request.urlopen",
        side_effect=error.HTTPError(
            url="http://127.0.0.1:11434/generate",
            code=503,
            msg="service unavailable",
            hdrs=None,
            fp=None,
        ),
    ):
        with pytest.raises(HTTPAIClientError, match="status 503"):
            client.generate_response("hello")


def test_http_ai_client_raises_on_socket_timeout() -> None:
    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.0)

    with patch("urllib.request.urlopen", side_effect=socket.timeout("timed out")):
        with pytest.raises(HTTPAIClientError, match="timed out"):
            client.generate_response("hello")


def test_http_ai_client_raises_on_invalid_json() -> None:
    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.0)

    with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse("not-json", status=200)):
        with pytest.raises(HTTPAIClientError, match="not valid JSON"):
            client.generate_response("hello")


def test_http_ai_client_raises_when_response_field_missing() -> None:
    client = HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=1.0)

    with patch("urllib.request.urlopen", return_value=_FakeHTTPResponse('{"message": "ok"}', status=200)):
        with pytest.raises(HTTPAIClientError, match="missing 'response' text"):
            client.generate_response("hello")


def test_http_ai_client_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="greater than 0"):
        HTTPAIClient(base_url="http://127.0.0.1:11434", timeout_seconds=0)

