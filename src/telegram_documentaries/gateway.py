from __future__ import annotations

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from . import settings
from .handlers import handle_photo, handle_restart
from .text_handler import handle_text

LOGGER = logging.getLogger("telegram_documentaries")


class _RedactToken(logging.Filter):
    """Strip the bot token from any log line before it is emitted."""

    def __init__(self, token: str) -> None:
        super().__init__()
        self._token = token

    def filter(self, record: logging.LogRecord) -> bool:
        if self._token:
            message = record.getMessage()
            if self._token in message:
                record.msg = message.replace(self._token, "***REDACTED***")
                record.args = None
        return True


def _configure_logging(token: str | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    # The Telegram Bot API embeds the token in request URLs, which httpx logs at
    # INFO. Keep transport logs quiet so secrets never reach the log file.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    if token:
        logging.getLogger().addFilter(_RedactToken(token))


def main() -> None:
    try:
        s = settings.load_settings()
    except Exception:
        _configure_logging()
        LOGGER.exception("event=gateway.config.error")
        raise
    _configure_logging(s.telegram_bot_token)
    LOGGER.info("event=gateway.configured")

    app = Application.builder().token(s.telegram_bot_token).build()
    app.add_handler(CommandHandler(["start", "restart"], handle_restart))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    LOGGER.info("event=gateway.polling.started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
