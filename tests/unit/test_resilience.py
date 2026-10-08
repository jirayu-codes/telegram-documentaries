from __future__ import annotations

import asyncio
import os
import tempfile
from types import SimpleNamespace
from typing import Any, cast

from telegram import Update
from telegram.ext import ContextTypes

from telegram_documentaries import handlers, state, text_handler


class FakeFile:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def download_as_bytearray(self) -> bytearray:
        return bytearray(self._data)


class FakeBot:
    def get_file(self, file_id: str) -> FakeFile:
        _ = file_id
        return FakeFile(b"img")

    async def send_message(self, chat_id: int | str, text: str) -> None:
        _ = (chat_id, text)

    async def send_photo(self, chat_id: int | str, photo: Any) -> None:
        _ = (chat_id, photo)

    async def send_voice(self, chat_id: int | str, voice: Any, **kwargs: Any) -> None:
        _ = (chat_id, voice, kwargs)


class FakeMsg:
    def __init__(self, text: str = "", has_photo: bool = False) -> None:
        self.text = text
        self.photo = [SimpleNamespace(file_id="fid")] if has_photo else None
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class FakeUpdate:
    def __init__(self, msg: FakeMsg, chat_id: int = 777) -> None:
        self.effective_message = msg
        self.effective_chat = SimpleNamespace(id=chat_id)
        self.effective_user = SimpleNamespace(id=1)
        self.update_id = 1


class FakeContext:
    def __init__(self) -> None:
        self.bot = FakeBot()


def _run(coro: Any) -> None:
    asyncio.run(coro)


def test_purge_deletes_temp_files() -> None:
    fd, path = tempfile.mkstemp(suffix=".ogg")
    os.close(fd)
    st = state.state.get("purge-test")
    st["audio_path"] = path
    st["photo_bytes"] = b"x"
    state.state.purge("purge-test")
    assert not os.path.exists(path)
    assert state.state.get("purge-test") == {}


def test_restart_command_purges_and_greets() -> None:
    st = state.state.get(7101)
    st["audio_path"] = "/tmp/does-not-exist.ogg"
    st["interview"] = {"phase": "AWAITING_ANSWER_2"}
    update = cast(Update, FakeUpdate(FakeMsg(), chat_id=7101))
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())

    _run(handlers.handle_restart(update, context))

    replies = cast(Any, update).effective_message.replies
    assert any("Session reset" in r for r in replies)
    assert state.state.get(7101) == {}


def test_text_before_photo_asks_for_portrait() -> None:
    state.state.reset(7102)
    update = cast(Update, FakeUpdate(FakeMsg(text="hello"), chat_id=7102))
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())

    _run(text_handler.handle_text(update, context))

    replies = cast(Any, update).effective_message.replies
    assert any("portrait photo" in r for r in replies)


def test_photo_mid_interview_is_rejected() -> None:
    st = state.state.get(7103)
    st["interview"] = {"phase": "AWAITING_ANSWER_2"}
    update = cast(Update, FakeUpdate(FakeMsg(has_photo=True), chat_id=7103))
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())

    _run(handlers.handle_photo(update, context))

    replies = cast(Any, update).effective_message.replies
    assert any("mid-interview" in r for r in replies)
