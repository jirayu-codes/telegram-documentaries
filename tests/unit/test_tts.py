from __future__ import annotations

import os

import pytest

from telegram_documentaries import tts


class FakeTTS:
    def synthesize_voice(self, script: str) -> bytes:
        return b"OggS" + script.encode("utf-8")[:5]


def test_tts() -> None:
    tts.set_tts(FakeTTS())
    out = tts.synthesize_voice("hello")
    assert out.startswith(b"OggS")


def test_write_temp_ogg() -> None:
    path = tts.write_temp_ogg(b"OggSdata")
    try:
        assert path.endswith(".ogg")
        with open(path, "rb") as f:
            assert f.read().startswith(b"OggS")
    finally:
        os.unlink(path)


def test_encode_ogg_from_pcm() -> None:
    pcm = b"\x00\x01" * 4800  # ~0.1s of 24kHz 16-bit mono silence-ish
    ogg = tts._encode_ogg(pcm)
    assert ogg.startswith(b"OggS")


def test_synthesize_voice_returns_empty_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from telegram_documentaries import settings

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("no settings")

    monkeypatch.setattr(settings, "load_settings", boom)
    assert tts._GeminiTTSImpl().synthesize_voice("hello") == b""
