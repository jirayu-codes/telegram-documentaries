# Requirements — Scripter (Phase 5)

## Scope
Generate dramatic, comedic British nature documentary narration (1 paragraph, max 90 words) from Interviewer's personality summary using Gemini 3.1 Flash Lite.

## Decisions
- Model: gemini-3.1-flash-lite
- Input: dossier/summary from interviewer state
- System/persona: dramatic British wildlife documentary narrator observing "wild beast" (human quirks as animal behaviors)
- Output: exactly 1 paragraph, max 90 words, no markdown
- Wire after interview completes (alongside converter) to send script to Telegram and store in state for TTS
