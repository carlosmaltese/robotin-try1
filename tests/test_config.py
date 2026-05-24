from pathlib import Path

from robotin.config import load_config


def _write_env(tmp_path: Path, content: str) -> Path:
    env_file = tmp_path / ".env"
    env_file.write_text(content, encoding="utf-8")
    return env_file


def test_load_config_returns_defaults_when_no_env(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    config = load_config(env_file=tmp_path / "nonexistent.env")

    assert config.ai_mode == "mock"
    assert config.ai_base_url == "http://127.0.0.1:8000"
    assert config.ai_timeout_seconds == 3.0
    assert config.stt_mode == "mock"
    assert config.stt_base_url == "http://127.0.0.1:8010"
    assert config.stt_timeout_seconds == 3.0
    assert config.log_level == "INFO"


def test_load_config_reads_env_file(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(
        tmp_path,
        "ROBOTIN_AI_MODE=http\nROBOTIN_AI_BASE_URL=http://192.168.1.10:8080\nROBOTIN_AI_TIMEOUT_SECONDS=5.0\n"
        "ROBOTIN_STT_MODE=remote\nROBOTIN_STT_BASE_URL=http://192.168.1.11:8090\nROBOTIN_STT_TIMEOUT_SECONDS=4.0\n",
    )
    config = load_config(env_file=env_file)

    assert config.ai_mode == "http"
    assert config.ai_base_url == "http://192.168.1.10:8080"
    assert config.ai_timeout_seconds == 5.0
    assert config.stt_mode == "remote"
    assert config.stt_base_url == "http://192.168.1.11:8090"
    assert config.stt_timeout_seconds == 4.0


def test_load_config_ignores_comments_and_blank_lines(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    content = (
        "# This is a comment\n\nROBOTIN_AI_BASE_URL=http://10.0.0.1:9000\n# another comment\n\n"
    )
    env_file = _write_env(tmp_path, content)
    config = load_config(env_file=env_file)

    assert config.ai_base_url == "http://10.0.0.1:9000"


def test_load_config_env_var_wins_over_env_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ROBOTIN_AI_MODE", "mock")
    monkeypatch.setenv("ROBOTIN_AI_BASE_URL", "http://from-shell:1234")
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("ROBOTIN_STT_MODE", "mock")
    monkeypatch.setenv("ROBOTIN_STT_BASE_URL", "http://stt-from-shell:1234")
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(
        tmp_path,
        "ROBOTIN_AI_BASE_URL=http://from-file:5678\nROBOTIN_STT_BASE_URL=http://stt-from-file:4321\n",
    )
    config = load_config(env_file=env_file)

    assert config.ai_base_url == "http://from-shell:1234"
    assert config.stt_base_url == "http://stt-from-shell:1234"


def test_load_config_reads_log_level_from_env_file(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_LOG_LEVEL=DEBUG\n")
    config = load_config(env_file=env_file)

    assert config.log_level == "DEBUG"


def test_load_config_rejects_invalid_log_level(tmp_path, monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_LOG_LEVEL=INVALID\n")

    with pytest.raises(ValueError, match="must be one of"):
        load_config(env_file=env_file)


def test_load_config_rejects_invalid_ai_mode(tmp_path, monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_AI_MODE=invalid\n")

    with pytest.raises(ValueError, match="ROBOTIN_AI_MODE must be one of"):
        load_config(env_file=env_file)


def test_load_config_rejects_non_positive_timeout(tmp_path, monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_AI_TIMEOUT_SECONDS=0\n")

    with pytest.raises(ValueError, match="must be greater than 0"):
        load_config(env_file=env_file)


def test_load_config_rejects_invalid_stt_mode(tmp_path, monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_STT_MODE=invalid\n")

    with pytest.raises(ValueError, match="ROBOTIN_STT_MODE must be one of"):
        load_config(env_file=env_file)


def test_load_config_rejects_non_positive_stt_timeout(tmp_path, monkeypatch) -> None:
    import pytest

    monkeypatch.delenv("ROBOTIN_AI_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_AI_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_MODE", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_BASE_URL", raising=False)
    monkeypatch.delenv("ROBOTIN_STT_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("ROBOTIN_LOG_LEVEL", raising=False)

    env_file = _write_env(tmp_path, "ROBOTIN_STT_TIMEOUT_SECONDS=0\n")

    with pytest.raises(ValueError, match="ROBOTIN_STT_TIMEOUT_SECONDS must be greater than 0"):
        load_config(env_file=env_file)
