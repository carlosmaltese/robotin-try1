import os
from dataclasses import dataclass
from pathlib import Path


AI_MODE_MOCK = "mock"
AI_MODE_HTTP = "http"
AI_MODE_VALUES = {AI_MODE_MOCK, AI_MODE_HTTP}
STT_MODE_MOCK = "mock"
STT_MODE_REMOTE = "remote"
STT_MODE_VALUES = {STT_MODE_MOCK, STT_MODE_REMOTE}

@dataclass(frozen=True)
class RobotinConfig:
    ai_mode: str = AI_MODE_MOCK
    ai_base_url: str = "http://127.0.0.1:8000"
    ai_timeout_seconds: float = 3.0
    stt_mode: str = STT_MODE_MOCK
    stt_base_url: str = "http://127.0.0.1:8010"
    stt_timeout_seconds: float = 3.0
    log_level: str = "INFO"


def _parse_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def load_config(env_file: Path | None = None) -> RobotinConfig:
    if env_file is None:
        default_env = Path(__file__).parent.parent.parent / ".env"
        if default_env.exists():
            env_file = default_env

    if env_file is not None and env_file.exists():
        for key, value in _parse_env_file(env_file).items():
            if key not in os.environ:
                os.environ[key] = value  # pragma: no cover

    log_level = os.environ.get("ROBOTIN_LOG_LEVEL", "INFO")
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_levels:
        raise ValueError(f"ROBOTIN_LOG_LEVEL must be one of {valid_levels}, got: {log_level!r}")

    ai_mode = os.environ.get("ROBOTIN_AI_MODE", AI_MODE_MOCK).strip().lower()
    if ai_mode not in AI_MODE_VALUES:
        allowed = ", ".join(sorted(AI_MODE_VALUES))
        raise ValueError(f"ROBOTIN_AI_MODE must be one of {{{allowed}}}, got: {ai_mode!r}")

    ai_base_url = os.environ.get("ROBOTIN_AI_BASE_URL", "http://127.0.0.1:8000").strip()
    if not ai_base_url:
        raise ValueError("ROBOTIN_AI_BASE_URL must not be empty")

    raw_timeout = os.environ.get("ROBOTIN_AI_TIMEOUT_SECONDS", "3.0")
    try:
        ai_timeout_seconds = float(raw_timeout)
    except ValueError as exc:
        raise ValueError("ROBOTIN_AI_TIMEOUT_SECONDS must be a valid number") from exc

    if ai_timeout_seconds <= 0:
        raise ValueError("ROBOTIN_AI_TIMEOUT_SECONDS must be greater than 0")

    stt_mode = os.environ.get("ROBOTIN_STT_MODE", STT_MODE_MOCK).strip().lower()
    if stt_mode not in STT_MODE_VALUES:
        allowed = ", ".join(sorted(STT_MODE_VALUES))
        raise ValueError(f"ROBOTIN_STT_MODE must be one of {{{allowed}}}, got: {stt_mode!r}")

    stt_base_url = os.environ.get("ROBOTIN_STT_BASE_URL", "http://127.0.0.1:8010").strip()
    if not stt_base_url:
        raise ValueError("ROBOTIN_STT_BASE_URL must not be empty")

    raw_stt_timeout = os.environ.get("ROBOTIN_STT_TIMEOUT_SECONDS", "3.0")
    try:
        stt_timeout_seconds = float(raw_stt_timeout)
    except ValueError as exc:
        raise ValueError("ROBOTIN_STT_TIMEOUT_SECONDS must be a valid number") from exc

    if stt_timeout_seconds <= 0:
        raise ValueError("ROBOTIN_STT_TIMEOUT_SECONDS must be greater than 0")

    return RobotinConfig(
        ai_mode=ai_mode,
        ai_base_url=ai_base_url,
        ai_timeout_seconds=ai_timeout_seconds,
        stt_mode=stt_mode,
        stt_base_url=stt_base_url,
        stt_timeout_seconds=stt_timeout_seconds,
        log_level=log_level,
    )
