from __future__ import annotations

import asyncio
from typing import Any, cast

from telegram.ext import ContextTypes

from telegram_documentaries import converter, scripter, state, text_handler, tts


class _FailingPhotoBot:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.voices: int = 0

    async def send_photo(self, **kwargs: Any) -> None:
        raise RuntimeError("photo boom")

    async def send_message(self, **kwargs: Any) -> None:
        self.messages.append(str(kwargs.get("text", "")))

    async def send_voice(self, **kwargs: Any) -> None:
        self.voices += 1


class _Context:
    def __init__(self, bot: _FailingPhotoBot) -> None:
        self.bot = bot


class _Conv:
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes:
        return b"IMG"


class _Scr:
    def generate_script(self, summary: str) -> str:
        return "The remarkable script"


class _NoAudio:
    def synthesize_voice(self, script: str) -> bytes:
        return b""


def test_delivery_continues_after_photo_failure() -> None:
    converter.set_converter(_Conv())
    scripter.set_scripter(_Scr())
    tts.set_tts(_NoAudio())

    st = state.state.get(9001)
    st["photo_bytes"] = b"x"
    st["interview"] = {"dossier": "d"}
    bot = _FailingPhotoBot()
    context = cast(ContextTypes.DEFAULT_TYPE, _Context(bot))

    asyncio.run(text_handler._deliver_documentary(context, 9001, st))

    assert "The remarkable script" in bot.messages
    assert any("narrator" in m for m in bot.messages)
    assert bot.voices == 0
