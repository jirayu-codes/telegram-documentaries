# The Telegram Documentaries

Send a portrait photo to a Telegram bot. It interviews you, renders you as a
hybrid animal, and narrates a dramatic wildlife documentary about you — as a
Telegram voice note.

The narration is delivered in the voice of a **dramatic British naturalist**:
hushed awe, present tense, you observed as a specimen in your natural habitat.

## Project status

✅ **Fully implemented (Phases 1–7).** All tests pass and all hooks are green.

| Piece | State |
| --- | --- |
| Constitution (`MISSION.md`, `TECH.md`, `ROADMAP.md`) | ✅ Complete |
| `scripts/test`, `scripts/hooks` | ✅ Working |
| Application code | ✅ Complete |

Check [`SPECS/ROADMAP.md`](SPECS/ROADMAP.md) for the full build order.

## How it works

A hub-and-spoke pipeline. The **Interviewer** orchestrates the conversation state;
specialist modules handle Bouncer, Converter, and Scripter. Narration uses direct
TTS.

| # | Stage | Model | What it does |
| --- | --- | --- | --- |
| 1 | **Bouncer** | Gemini 3.1 Flash Lite (vision) | Confirms the image contains a human. Rejects non-human images with a cheeky response and resets the run. |
| 2 | **Interviewer** *(orchestrator)* | Gemini 3.1 Flash Lite | Asks 5–7 questions, one per turn, builds a behavioural dossier keyed by `chat_id`, and suggests an animal. |
| 3 | **Converter** | Gemini 3.1 Flash Image | Fuses the original photo and the dossier into a hybrid animal portrait and sends it directly to the chat. |
| 4 | **Scripter** | Gemini 3.1 Flash Lite | Writes one dramatic 60–90 word nature-documentary paragraph from the dossier. |
| 5 | **Narrator** | `gemini-3.1-flash-tts-preview` | Renders that paragraph to an OGG/OPUS voice note and sends it via Telegram. |

Transport is Telegram **long polling** (`getUpdates`). Session state is held
**in memory**, keyed by `chat_id`, and is purged by `/start` or `/restart`
without restarting the process. Robust guards handle out-of-order input.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended)
- [`gitleaks`](https://github.com/gitleaks/gitleaks) (required for hooks)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
# 1. Clone
git clone https://github.com/jirayu-codes/telegram-documentaries.git
cd telegram-documentaries

# 2. Create your local environment file
cp .env.example .env

# 3. Fill in your keys
$EDITOR .env

# 4. Sync dependencies
uv sync
```

`.env` is gitignored and must never be committed. `.env.example` carries
placeholders only.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Auth token for the Telegram Bot API. |
| `GEMINI_API_KEY` | Yes | Google Gemini API key used for all model calls. |

## Running the bot

```bash
# Run the Telegram bot (long polling)
uv run telegram-documentaries
```

## Development scripts

| Script | Runs | Purpose |
| --- | --- | --- |
| `scripts/test` | pytest | Run the full test suite (27 unit/integration tests). |
| `scripts/hooks` | pytest + ruff + ruff-format + mypy + gitleaks | The full pre-commit suite. |

Both scripts are the ground truth. Never bypass them with ad-hoc commands.

## Testing philosophy

- **Red/Green TDD.** Tests are written to drive behaviour.
- `tests/unit/` — pure logic (state machine, contracts, parsers); no network.
- `tests/integration/` — wiring with Telegram/Gemini faked at boundaries.
- The suite **never makes live network calls**.

## Project structure

```
telegram-documentaries/
├── SPECS/                  # Constitution + per-phase specs
├── src/telegram_documentaries/
├── scripts/                # test + hooks
└── tests/                  # unit + integration
```

## End-to-end usage

1. Send `/start` (or `/restart`) to the bot.
2. Send a **human** portrait photo — the Bouncer validates and proceeds.
3. Answer **5–7** questions, one per turn — the Interviewer builds your dossier.
4. Receive your **hybrid animal portrait**.
5. Receive a **60–90 word dramatic narration script**.
6. Receive a **British-narrator voice note** (OGG/OPUS).
7. Type `/restart` to start fresh at any time.

Non-human photos are rejected politely. The bot handles out-of-order text/photo
gracefully and never requires a process restart.

## Specifications

- **[`SPECS/MISSION.md`](SPECS/MISSION.md)** — product contract, in/out of scope.
- **[`SPECS/TECH.md`](SPECS/TECH.md)** — stack, architecture, policies.
- **[`SPECS/ROADMAP.md`](SPECS/ROADMAP.md)** — ordered build plan.
- Per-phase specs: `SPECS/YYYY-MM-DD-<feature>/` (`requirements.md`, `plan.md`,
  `validation.md`).
