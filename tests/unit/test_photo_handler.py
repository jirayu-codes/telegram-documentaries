import asyncio
from types import SimpleNamespace
from typing import Any, cast

from telegram import Update
from telegram.ext import ContextTypes

from telegram_documentaries import bouncer, handlers, state
from telegram_documentaries.types import ClassificationResult


class FakeClassifier:
    def __init__(self, is_human: bool) -> None:
        self.is_human = is_human

    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        return ClassificationResult(is_human=self.is_human, reason="ok")


class FakeFile:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def download_as_bytearray(self) -> bytearray:
        return bytearray(self._data)


class FakeBot:
    def get_file(self, file_id: str) -> FakeFile:
        assert file_id == "fid"
        return FakeFile(b"img")


class FakeMsg:
    def __init__(self, is_human: bool) -> None:
        self.is_human = is_human
        self.photo = [SimpleNamespace(file_id="fid")]
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class FakeUpdate:
    def __init__(self, is_human: bool) -> None:
        self.effective_message = FakeMsg(is_human)
        self.effective_chat = SimpleNamespace(id=42)
        self.effective_user = SimpleNamespace(id=1)
        self.update_id = 1


class FakeContext:
    def __init__(self) -> None:
        self.bot = FakeBot()


def test_photo_handler_routes_to_approve() -> None:
    state.state.reset(42)
    bouncer.set_classifier(FakeClassifier(True))
    update = cast(Update, FakeUpdate(True))
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())

    async def run() -> None:
        await handlers.handle_photo(update, context)

    asyncio.run(run())
    replies = cast(Any, cast(Any, update).effective_message).replies
    assert any("Human detected" in r for r in replies)


def test_photo_handler_routes_to_reject() -> None:
    state.state.reset(42)
    bouncer.set_classifier(FakeClassifier(False))
    update = cast(Update, FakeUpdate(False))
    context = cast(ContextTypes.DEFAULT_TYPE, FakeContext())

    async def run() -> None:
        await handlers.handle_photo(update, context)

    asyncio.run(run())
    msgs = cast(Any, cast(Any, update).effective_message).replies
    needle = "don't think that's human"
    assert any(needle in r for r in msgs)
