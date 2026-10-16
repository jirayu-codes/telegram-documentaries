from __future__ import annotations

import logging

from telegram_documentaries.gateway import _RedactToken

TOKEN = "123456:AAExampleTokenValue"


def _record(message: str, *args: object) -> logging.LogRecord:
    return logging.LogRecord("x", logging.INFO, __file__, 1, message, args, None)


def test_redact_token_in_plain_message() -> None:
    filt = _RedactToken(TOKEN)
    rec = _record("polling https://api.telegram.org/bot%s/getMe", TOKEN)
    assert filt.filter(rec) is True
    assert TOKEN not in rec.getMessage()
    assert "***REDACTED***" in rec.getMessage()


def test_redact_leaves_other_messages() -> None:
    filt = _RedactToken(TOKEN)
    rec = _record("nothing secret here")
    assert filt.filter(rec) is True
    assert rec.getMessage() == "nothing secret here"


def test_redact_noop_without_token() -> None:
    filt = _RedactToken("")
    rec = _record("still fine")
    assert filt.filter(rec) is True
    assert rec.getMessage() == "still fine"
