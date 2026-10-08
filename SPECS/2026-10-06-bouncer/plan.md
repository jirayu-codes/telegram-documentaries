# Plan — Bouncer (Phase 2)

Red/Green TDD: write failing tests (group 3), observe FAIL, then implement.

## 1. Dependencies & config
1.1 Add `google-generativeai` to dependencies (or google-genai). Update pyproject + uv.lock.
1.2 Extend settings if needed (GEMINI_API_KEY already present). No secrets changes.

## 2. Contracts & types
2.1 `src/telegram_documentaries/types.py` (or models): PhotoPayload (chat_id, file_id, bytes, mime), ClassificationResult (is_human: bool, reason: str).
2.2 `src/telegram_documentaries/state.py`: minimal in-memory per-chat state (dict) + reset(chat_id) and clear_all(). Versioned conceptually, in-memory only.

## 3. Red — failing tests
3.1 `tests/unit/test_bouncer_classify.py`: mock Gemini returns is_human True/False with reasons.
3.2 `tests/unit/test_bouncer_reject.py`: rejection message is cheeky and explains why.
3.3 `tests/unit/test_bouncer_state.py`: reset() clears ephemeral state.
3.4 `tests/unit/test_photo_handler.py`: photo download mocked; routes to approve/reject.
3.5 `tests/integration/test_bouncer_integration.py`: wiring works with fakes.
Run tests → FAIL.

## 4. Green — implementation
4.1 `src/telegram_documentaries/bouncer.py`: classify(image_bytes, mime) calls Gemini 3.1 Flash Lite via interface; returns ClassificationResult.
4.2 `src/telegram_documentaries/photo.py`: download photo from Telegram (via bot API), handle failures.
4.3 `src/telegram_documentaries/handlers.py`: photo handler routes: human → approve (proceed), non-human → reject + reset state. Structured logging via decorators.
4.4 Wire into gateway (handle photo updates).

## 5. Tests pass, hooks pass
5.1 `scripts/test` passes; `scripts/hooks` (all 5) passes.

## 6. Docs/spec reconciliation
6.1 Update README if behavior changes. No ROADMAP mark yet.
