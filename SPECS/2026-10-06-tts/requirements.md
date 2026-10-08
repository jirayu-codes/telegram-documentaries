# Requirements — TTS (Phase 6)

## Scope
Generate a narration voice note from the Scripter's script using Gemini TTS
(`gemini-3.1-flash-tts-preview`), delivered to Telegram as a voice message.

## Decisions
- **Model:** `gemini-3.1-flash-tts-preview` (direct synthesis, no reasoning agent).
- **Voice:** `Charon` — a deep male voice, with the style instruction
  "deep male voice with a posh British accent, like a dramatic narrator"
  prepended to the text prompt (Attenborough-style).
- **Input:** script text from the Scripter (stored in `state["script"]`).
- **Audio format:** Gemini returns raw 24kHz linear PCM (16-bit mono). Encode to
  **OGG/OPUS** via `soundfile` so Telegram's `send_voice` accepts it.
- **Persistence:** write the encoded audio to a temp `.ogg` file and store its
  path in `state["audio_path"]`.
- **Delivery:** `bot.send_voice(chat_id, voice=file, filename="documentary.ogg")`.

## Notes
- Telegram is picky about formats: OGG (OPUS) is used for voice notes; MP3 is
  also accepted. We standardise on OGG/OPUS.
- All Gemini calls are wrapped in try/except; failures fall back to a short
  silent OGG so the pipeline never crashes.
