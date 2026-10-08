from __future__ import annotations

import asyncio
import inspect

import pytest

from telegram_documentaries import logging as tlog


def test_structured_logging_decorator_preserves_result_and_emits(
    caplog: pytest.LogCaptureFixture,
) -> None:
    @tlog.log_call("test.op")
    def op(x: int) -> int:
        return x + 1

    with caplog.at_level("INFO"):
        assert op(2) == 3
    records = caplog.records
    messages = [r.getMessage() for r in records]
    assert any("event=test.op" in m for m in messages)


def test_structured_logging_decorator_keeps_handlers_async() -> None:
    @tlog.log_call("test.async_op")
    async def op(x: int) -> int:
        return x + 1

    assert inspect.iscoroutinefunction(op) is True
    assert asyncio.run(op(2)) == 3


def test_structured_logging_decorator_logs_and_reraises_async_failures(
    caplog: pytest.LogCaptureFixture,
) -> None:
    @tlog.log_call("test.async_boom")
    async def boom() -> None:
        raise ValueError("kaboom")

    with caplog.at_level("INFO"):
        with pytest.raises(ValueError, match="kaboom"):
            asyncio.run(boom())

    messages = [r.getMessage() for r in caplog.records]
    assert any("event=test.async_boom error" in m for m in messages)
    assert any(record.exc_info is not None for record in caplog.records)
