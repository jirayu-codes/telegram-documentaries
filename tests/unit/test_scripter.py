from __future__ import annotations

import pytest

from telegram_documentaries import gemini, scripter


class FakeScr:
    def generate_script(self, summary: str) -> str:
        return f"Ah, behold the rare {summary}... most peculiar!"


def test_generate_script() -> None:
    scripter.set_scripter(FakeScr())
    out = scripter.generate_script("subject")
    assert "subject" in out


def test_generate_script_falls_back_when_model_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(gemini, "generate_text", lambda *a, **k: "")
    out = scripter._GeminiImpl().generate_script("subject")
    assert out.strip() != ""
