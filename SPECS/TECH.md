# TECH

The technical contract. Feature specs, implementation, review, and verification
all defer to this file.

## Stack

| Concern | Choice |
| --- | --- |
| Language | Python 3.11+ |
| Transport | Telegram Bot API, **long polling** (`getUpdates`). No webhooks. |
| Agent framework | Google ADK, hub-and-spoke |
| Vision gate / interview / script | Gemini 3.1 Flash Lite |
| Image synthesis | Gemini 3.1 Flash Image |
| Text-to-speech | `gemini-3.1-flash-tts-preview` |
| Boundary models | Pydantic |
| Test / lint / types | pytest + ruff + mypy |

Secrets come from `.env` — `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`. Never
hardcoded, never committed.

## Architecture

ADK **hub-and-spoke**. One orchestrator owns the Telegram conversation state
and delegates to specialist agents:

- **The Interviewer** *is* the orchestrator. It drives the state machine, asks
  the 5–7 questions one at a time, and accumulates the dossier.
- **The Bouncer** — vision gate; rejects non-human images and resets the run.
- **The Converter** — multimodal fusion of photo + dossier into a hybrid
  animal portrait, sent to Telegram directly with no intermediate text hop.
- **The Scripter** — one 60–90 word dramatic paragraph derived from the
  dossier.

**The Narrator is not an agent.** TTS is an execution tool: the orchestrator
forwards the Scripter's text to the Gemini TTS endpoint and sends the resulting
audio.

Each stage is a discrete module with a single job. Stages do not call each
other directly; the orchestrator routes.

### State machine

Exactly one phase per `chat_id`. These phases are normative:

| Phase | Meaning |
| --- | --- |
| `IDLE` | No run in progress. |
| `AWAITING_PHOTO` | Greeted; waiting for a media message. |
| `BOUNCING` | Photo received; vision gate in flight. |
| `INTERVIEWING` | Asking question *n* of 5–7; dossier accumulating. |
| `CONVERTING` | Interview complete; image synthesis in flight. |
| `SCRIPTING` | Composing the narration paragraph. |
| `NARRATING` | TTS rendering and audio delivery. |
| `DONE` | Artifacts delivered; awaiting a new photo or `/restart`. |

Transitions out of `BOUNCING` on rejection purge the run and return to
`AWAITING_PHOTO`, so a valid photo can be sent without re-typing `/start`.
`/start` and `/restart` purge the run and return to `IDLE`.

Feature specs may add transition detail, but may not remove or rename phases
without amending this file.

## Contracts at boundaries

- Parse Telegram updates, Gemini responses, and TTS output into **typed
  Pydantic models at the edge**. Never pass raw dicts or unvalidated payloads
  across a module boundary.
- Treat all external input — Telegram updates, model output, file bytes — as
  untrusted and arbitrary.

## Logging & error policy

- Comprehensive **structured** logging. Prefer decorators over weaving logging
  into business logic.
- **Fail loudly and log** for non-critical, user-invisible work.
- On a validated user's conversation path, **catch and degrade gracefully** so
  the conversation continues — logged loudly, never raising into the user's
  flow.
- **No** bare `except: pass`, **no** swallowed exceptions, **no** unlogged
  fallbacks.

## Session state

- A versioned, per-`chat_id` schema with **one shared state driver** for the
  whole pipeline. No module keeps private session state.
- In-memory only. A process restart forgets every session (see the MISSION.md
  out-of-scope list).
- **Reset semantics:** `/start` and `/restart` purge session state and
  temporary media without restarting the process.

## Testing

- **Red/Green TDD.** Tests are written before code; a test must fail before it
  passes.
- Dev scripts in `scripts/` are the **ground truth** for tests, lint, and type
  checks:
  - `scripts/test` — run the suite (pytest).
  - `scripts/hooks` — the full pre-commit suite (pytest + ruff + mypy).
- Never bypass these scripts with ad-hoc `pytest` / `ruff` / `mypy`
  invocations.
- Both scripts are documented in `README.md` and kept in sync with it.

## Repo hygiene

- `.env` is in `.gitignore`. `.env.example` carries placeholders only.
- Reproducible environment: dependencies are locked and the lockfile is
  committed.

## README policy

`README.md` documents developer-facing behaviour — setup, the `.env`
variables, the `scripts/` entry points, and the pipeline overview. It must be
updated in the same change that alters the behaviour it describes.
