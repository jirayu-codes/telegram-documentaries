from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from . import logging as tlog
from . import reply, settings

LOGGER = logging.getLogger("telegram_documentaries")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@tlog.log_call("gateway.handle_text")
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    try:
        msg = reply.handle_text_message()
    except Exception:
        LOGGER.exception("event=gateway.handle_text.error")
        return

    try:
        if update.effective_message is None:
            return
        await update.effective_message.reply_text(msg)
    except Exception:
        LOGGER.exception("event=gateway.reply.error")
        return


def main() -> None:
    _configure_logging()
    try:
        s = settings.load_settings()
        LOGGER.info("event=gateway.configured")
    except Exception:
        LOGGER.exception("event=gateway.config.error")
        raise

    app = Application.builder().token(s.telegram_bot_token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND, handle_text))
    LOGGER.info("event=gateway.polling.started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
