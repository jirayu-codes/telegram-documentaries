from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from . import logging as tlog
from . import photo
from .bouncer import classify
from .state import state


@tlog.log_call("handlers.photo")
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.effective_message is None or update.effective_message.photo is None:
            return
        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        largest = update.effective_message.photo[-1]
        payload = photo.download_photo(context.bot, largest.file_id, chat_id)
        if payload is None:
            await update.effective_message.reply_text(
                "Hmm, couldn't load that photo. Try again."
            )
            return
        res = classify(payload.bytes, payload.mime)
        if res.is_human:
            await update.effective_message.reply_text(
                "Human detected. Ready to proceed."
            )
            state.reset(chat_id)
            return
        else:
            state.reset(chat_id)
            msg = f"Nice try, but I don't think that's human. {res.reason}"
            await update.effective_message.reply_text(msg)
            return
    except Exception:
        return
