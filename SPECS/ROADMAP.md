# ROADMAP

The ordered build plan. One phase per pipeline capability. Work proceeds top
to bottom; a phase is **complete only when the verifier has confirmed its
acceptance criteria**, at which point this file is updated.

Every phase is Red/Green TDD: the tests are written first and must fail before
they pass.

## Phases

| # | Phase | Scope | Acceptance criteria | Serves |
| --- | --- | --- | --- | --- |
| 1 | **Repository & gateway** | Project skeleton, `.env` loading, `scripts/test` + `scripts/hooks` in place, long-polling loop that replies with a hardcoded message | `scripts/test` and `scripts/hooks` both pass; the bot answers a message in Telegram | Foundation |
| 2 | **Bouncer** | Vision gate plus rejection and reset routing | A human photo proceeds to the interview; a non-human photo gets a cheeky rejection and the run resets | Rubric: intake |
| 3 | **Interviewer** | Sequential stateful Q&A (5–7 questions, one per turn), dossier summary, suggested animal | Dossier accumulates per `chat_id`; the interview completes and yields an animal | Rubric: conversation |
| 4 | **Converter** | Multimodal hybrid portrait delivered to Telegram | Photo + dossier synthesise to an image that arrives in the chat | Rubric: image |
| 5 | **Scripter** | One-paragraph narration | A 60–90 word dramatic paragraph derived from the dossier | Rubric: script |
| 6 | **Narrator** | TTS synthesis and audio delivery | Script text renders to OGG/MP3 and arrives as a voice note | Rubric: voice |
| 7 | **Resilience** | `/restart` and `/start` reset (cancel active session, purge temp files, re-initialise memory), wrong-payload-at-wrong-stage guards, API-timeout fallbacks | Out-of-order input is handled gracefully; reset works without restarting the process | Rubric: robustness |

## Test directory philosophy

- Tests live in `tests/`, mirroring the source layout one file per module.
- `tests/unit/` covers pure logic — the state machine, boundary contracts,
  parsers — with **no network access**.
- `tests/integration/` covers module wiring with Telegram and Gemini faked at
  their boundary contracts.
- The suite **never makes live network calls**. External services are replaced
  at the edge by the typed models defined in `SPECS/TECH.md`.

## Rules

- Do not start a phase before the previous one is verified.
- Do not mark a phase complete without running `scripts/test` and
  `scripts/hooks`.
- Adding, dropping, or reordering a phase requires amending this file.
