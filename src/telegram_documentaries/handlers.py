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
            q = interviewer.start_interview(chat_id)
            await update.effective_message.reply_text(q)
            state.reset(chat_id)  # ensure clean
            st = state.get(chat_id)
            st["interview"] = {
                "phase": "AWAITING_ANSWER_1",
                "q_index": 0,
                "history": [],
                "dossier": "",
                "suggested_animal": "",
                "question_count": 5,
                "current_question": q,
            }
            return
        else:
            state.reset(chat_id)
            msg = f"Nice try, but I don't think that's human. {res.reason}"
            await update.effective_message.reply_text(msg)
            return
    except Exception:
        return
