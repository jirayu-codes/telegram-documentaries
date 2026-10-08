# Requirements — Bouncer (Phase 2)

## Context
ROADMAP Phase 2: Bouncer — vision gate plus rejection and reset routing. The bot currently only responds to text with `hey mate!`. Now it must inspect incoming photo uploads with Gemini 3.1 Flash Lite and route accordingly.

Constitution references: MISSION.md (vision gate), TECH.md (hub-and-spoke, boundary contracts, logging, secrets), ROADMAP.md (Phase 2).

## Scope
1. Detect incoming photo messages (not just text). When a photo is received, download image bytes from Telegram.
2. Use **Gemini 3.1 Flash Lite** (vision) to classify: is there a discernible human subject present? Return a strict boolean/categorical decision.
3. On **human**: approve and trigger the pipeline confirmation step (for Phase 2, this means proceed to the next action; since Interviewer comes later, minimally produce a clear "approved/ready to proceed" outcome while still honoring existing behavior where appropriate).
4. On **non-human**: reject with a cheeky message explaining why (call out inanimate objects/animals etc), **reset any ephemeral conversation state**, and do not proceed.
5. Both paths must be logged (structured, via decorators per TECH.md). No secrets in logs.
6. Red/Green TDD. No network in unit tests; Gemini calls mocked at boundary.

## Decisions
- Use `google-generativeai` (or `google.genai`) to call Gemini 3.1 Flash Lite with image bytes. Keep Gemini calls behind an interface so tests can fake.
- Define typed contracts (Pydantic) at boundaries: photo payload (chat_id, file_id, bytes, mime), classification result (is_human: bool, reason: str).
- State reset: for Phase 2, "ephemeral conversation state" means any in-memory per-chat state we introduce now; if none exists yet, create a minimal per-chat state store with `reset(chat_id)`. Must not persist across restarts (in-memory only).
- Personality: cheeky but not cruel; explain rejection without sounding like HTTP errors.
- Handle multiple photos? Single photo per message is fine; if multiple, pick largest or just process first? Keep simple and general.

## Contracts (boundaries treated as untrusted)
- Telegram photo updates: may be missing fields; validate at edge. Download must handle failures gracefully (log loudly, degrade on conversation path).
- Gemini response: parse to typed model; treat arbitrary. Fail loud only if config missing; on classification call failure, log loudly and degrade gracefully to a safe rejection (don’t crash loop).
- All external I/O behind interfaces.

## Out of scope
- Interviewer, Converter, Scripter, Narrator (Phases 3+)
- Session state beyond minimal reset needed for this gate
- Video, voice input

## Non-functional
- Follow logging/error policy (structured, decorator-based; degrade gracefully on conversation path; fail loud on invisible work).
- No network in tests. `.env` remains untracked.
- Update README/TECH if needed (no spec conflict).
