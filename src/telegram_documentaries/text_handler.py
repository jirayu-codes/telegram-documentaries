from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from . import converter, interviewer, scripter, tts
from . import logging as tlog
from .state import state

LOGGER = logging.getLogger("telegram_documentaries")


@tlog.log_call("handlers.text")
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = update.effective_message
        if message is None:
            return
        chat_id = update.effective_chat.id if update.effective_chat else "unknown"
        st = state.get(chat_id)
        iv = st.get("interview")
        if iv and str(iv.get("phase", "")).startswith("AWAITING_ANSWER"):
            ans = message.text or ""
            res = interviewer.handle_answer(chat_id, ans)
            if res is None:
                return
            if "Dossier:" in res:
                await _deliver_documentary(context, chat_id, st)
                return
            await message.reply_text(res)
            return
        await message.reply_text(
            "Send me a clear portrait photo to start your wildlife documentary."
        )
    except Exception:
        LOGGER.exception("event=handlers.text.error")
        await _notify_error(update)
        return


async def _deliver_documentary(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int | str,
    st: dict[str, object],
) -> None:
    interview = st.get("interview")
    dossier = ""
    if isinstance(interview, dict):
        dossier = str(interview.get("dossier", ""))
    LOGGER.info("event=deliver.start dossier_len=%d", len(dossier))
    photo_bytes = st.get("photo_bytes")
    if isinstance(photo_bytes, (bytes, bytearray)):
        img = converter.generate_hybrid(bytes(photo_bytes), dossier)
        LOGGER.info("event=deliver.image bytes=%d", len(img))
        if img:
            await context.bot.send_photo(chat_id=chat_id, photo=img)
    script = scripter.generate_script(dossier)
    LOGGER.info("event=deliver.script chars=%d", len(script))
    st["script"] = script
    await context.bot.send_message(chat_id=chat_id, text=script)
    audio = tts.synthesize_voice(script)
    LOGGER.info("event=deliver.audio bytes=%d", len(audio))
    if not audio:
        await context.bot.send_message(
            chat_id=chat_id,
            text="(The narrator lost their voice — but the story lives on!)",
        )
        return
    path = tts.write_temp_ogg(audio)
    st["audio_path"] = path
    with open(path, "rb") as f:
        await context.bot.send_voice(
            chat_id=chat_id,
            voice=f,
            filename="documentary.ogg",
        )
    LOGGER.info("event=deliver.done")


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
