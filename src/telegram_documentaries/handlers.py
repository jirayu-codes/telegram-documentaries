from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from . import interviewer, photo
from . import logging as tlog
from .bouncer import classify
from .state import state


@tlog.log_call("handlers.photo")
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = update.effective_message
        if message is None or message.photo is None:
            return
        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        st = state.get(chat_id)
        iv = st.get("interview")
        if iv and str(iv.get("phase", "")).startswith("AWAITING_ANSWER"):
            await message.reply_text(
                "You're mid-interview! Answer the current question with text, "
                "or send /restart to start fresh."
            )
            return
        largest = message.photo[-1]
        payload = photo.download_photo(context.bot, largest.file_id, chat_id)
        if payload is None:
            await message.reply_text("Hmm, couldn't load that photo. Try again.")
            return
        res = classify(payload.bytes, payload.mime)
        if res.is_human:
            state.purge(chat_id)
            st = state.get(chat_id)
            st["photo_bytes"] = payload.bytes
            q = interviewer.start_interview(chat_id)
            await message.reply_text("Human detected. Ready to proceed.")
            await message.reply_text(q)
            return
        state.purge(chat_id)
        msg = f"Nice try, but I don't think that's human. {res.reason}"
        await message.reply_text(msg)
    except Exception:
        await _notify_error(update)
        return


@tlog.log_call("handlers.restart")
async def handle_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return
    chat_id = update.effective_chat.id if update.effective_chat else "unknown"
    state.purge(chat_id)
    await message.reply_text(
        "Session reset. Send a clear portrait photo to begin your documentary."
    )


async def _notify_error(update: Update) -> None:
    message = update.effective_message
    if message is None:
        return
    try:
        await message.reply_text(
            "Something went wrong on my end. Please try again or send /restart."
        )
    except Exception:
        return
