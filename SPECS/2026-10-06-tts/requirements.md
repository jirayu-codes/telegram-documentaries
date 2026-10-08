# Requirements — TTS (Phase 6)

## Scope
Generate voice note narration from script using Gemini TTS (Kore voice, 24kHz linear PCM or opus as appropriate).

## Decisions
- Use google.genai (or compatible) TTS with voice "Kore"
- Input: script text from scripter state
- Output: audio bytes/file sent as voice message to chat
- Store audio path in state (e.g., state["audio_path"]) for reference
