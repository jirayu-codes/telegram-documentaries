from pathlib import Path

import pytest

from telegram_documentaries import settings


def test_missing_telegram_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as exc:
        settings.load_settings(env_file=Path("/tmp/nonexistent.env"))
    assert "TELEGRAM_BOT_TOKEN" in str(exc.value)


def test_missing_gemini_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as exc:
        settings.load_settings(env_file=Path("/tmp/nonexistent.env"))
    assert "GEMINI_API_KEY" in str(exc.value)


def test_empty_values_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(RuntimeError):
        settings.load_settings(env_file=Path("/tmp/nonexistent.env"))


def test_bad_token_format_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "justatoken")
    monkeypatch.setenv("GEMINI_API_KEY", "key123")
    with pytest.raises(RuntimeError):
        settings.load_settings(env_file=Path("/tmp/nonexistent.env"))


def test_valid_settings_load(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABCDEF")
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyBqeYyGGk8YFniia0WMsKj6beBVcRU4MuA")
    s = settings.load_settings(env_file=Path("/tmp/nonexistent.env"))
    assert s.telegram_bot_token == "123456:ABCDEF"
    assert s.gemini_api_key == "AIzaSyBqeYyGGk8YFniia0WMsKj6beBVcRU4MuA"
