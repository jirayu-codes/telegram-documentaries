from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from . import interviewer, reply
from . import logging as tlog
from .state import state


@tlog.log_call("handlers.text")
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _ = context
    try:
        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        st = state.get(chat_id)
        iv = st.get("interview")
        if iv and iv.get("phase", "").startswith("AWAITING_ANSWER"):
            ans = update.effective_message.text if update.effective_message else ""
            res = interviewer.handle_answer(chat_id, ans)
            await update.effective_message.reply_text(res or "ok")
            return
        msg = reply.handle_text_message()
        await update.effective_message.reply_text(msg)
    except Exception:
        return
