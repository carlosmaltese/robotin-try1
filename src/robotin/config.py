import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RobotinConfig:
    ai_base_url: str = "http://127.0.0.1:8000"
    ai_timeout_seconds: float = 3.0
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

    return RobotinConfig(
        ai_base_url=os.environ.get("ROBOTIN_AI_BASE_URL", "http://127.0.0.1:8000"),
        ai_timeout_seconds=float(os.environ.get("ROBOTIN_AI_TIMEOUT_SECONDS", "3.0")),
        log_level=log_level,
    )
