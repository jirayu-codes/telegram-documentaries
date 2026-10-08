from __future__ import annotations

import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

from . import converter, interviewer, reply, scripter, state
from . import logging as tlog

log = tlog.get_logger(__name__)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else 0
    try:
        photo = (
            update.effective_message.photo[-1]
            if update.effective_message and update.effective_message.photo
            else None
        )
        if not photo:
            await reply.send_text(update, context, "Please send a photo.")
            return
        file = await context.bot.get_file(photo.file_id)
        fd, path = tempfile.mkstemp(suffix=".jpg")
        try:
            os.close(fd)
            await file.download_to_drive(path)
            with open(path, "rb") as f:
                image_bytes = f.read()
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass
        st = state.get(chat_id)
        st["photo_bytes"] = image_bytes
        q = interviewer.start_interview(chat_id, question_count=5)
        await reply.send_text(update, context, q)
    except Exception as e:
        log.exception("photo_handler_error", exc_info=e)
        await reply.send_text(update, context, "Photo processing error.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id if update.effective_chat else 0
    try:
        text = update.message.text if update.message and update.message.text else ""
        res = interviewer.handle_answer(chat_id, text)
        if res is None:
            await reply.send_text(update, context, "No active interview.")
            return
        if "Dossier:" in str(res):
            st = state.get(chat_id)
            photo_bytes = st.get("photo_bytes")
            iv = st.get("interview", {})
            dossier = iv.get("dossier", "")
            if photo_bytes:
                img = converter.generate_hybrid(bytes(photo_bytes), str(dossier))
                await context.bot.send_photo(chat_id=chat_id, photo=img)
            script = scripter.generate_script(str(dossier) or str(iv))
            st["script"] = script
            await reply.send_text(update, context, script)
            return
        await reply.send_text(update, context, res)
    except Exception as e:
        log.exception("text_handler_error", exc_info=e)
        await reply.send_text(update, context, "Interview error.")
