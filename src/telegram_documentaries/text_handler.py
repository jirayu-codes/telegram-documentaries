from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from . import converter, interviewer, reply, scripter, tts
from . import logging as tlog
from .state import state


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
                await _deliver_documentary(update, context, chat_id, st, res)
                return
            await message.reply_text(res)
            return
        msg = reply.handle_text_message()
        await message.reply_text(msg)
    except Exception:
        return


async def _deliver_documentary(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int | str,
    st: dict[str, object],
    res: str,
) -> None:
    message = update.effective_message
    if message is None:
        return
    interview = st.get("interview")
    dossier = ""
    if isinstance(interview, dict):
        dossier = str(interview.get("dossier", ""))
    photo_bytes = st.get("photo_bytes")
    if isinstance(photo_bytes, (bytes, bytearray)):
        img = converter.generate_hybrid(bytes(photo_bytes), dossier)
        await context.bot.send_photo(chat_id=chat_id, photo=img)
    script = scripter.generate_script(dossier)
    st["script"] = script
    await message.reply_text(script)
    audio = tts.synthesize_voice(script)
    if not audio:
        return
    path = tts.write_temp_ogg(audio)
    st["audio_path"] = path
    try:
        with open(path, "rb") as f:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=f,
                filename="documentary.ogg",
            )
    except Exception:
        return
