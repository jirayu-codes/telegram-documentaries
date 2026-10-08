# Requirements — Converter (Phase 4)

## Scope
Multimodal hybrid portrait using Gemini 3.1 Flash Image (photo + dossier) sent to Telegram.

## Decisions
- Use gemini-3.1-flash-image
- Input: original photo bytes + dossier text
- Output: image sent to chat
- Mock in tests (no network)
