from __future__ import annotations

import logging

from telegram.ext import Application, MessageHandler, filters

from . import settings
from .handlers import handle_photo
from .text_handler import handle_text

LOGGER = logging.getLogger("telegram_documentaries")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> None:
    _configure_logging()
    try:
        s = settings.load_settings()
        LOGGER.info("event=gateway.configured")
    except Exception:
        LOGGER.exception("event=gateway.config.error")
        raise

    app = Application.builder().token(s.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND, handle_text))
    LOGGER.info("event=gateway.polling.started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
