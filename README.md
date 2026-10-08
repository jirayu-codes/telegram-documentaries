# The Telegram Documentaries

Send a portrait photo to a Telegram bot. It interviews you, renders you as a
hybrid animal, and narrates a dramatic wildlife documentary about you — as a
Telegram voice note.

The narration is delivered in the voice of a **dramatic British naturalist**:
hushed awe, present tense, you observed as a specimen in your natural habitat.

## Project status

**Implemented (Phase 1).** The project constitution lives in [`SPECS/`](SPECS/)
and is the single source of truth for everything built from here. There is no
application code yet — no `src/`, `tests/`, or `scripts/`.

| Piece | State |
| --- | --- |
| Constitution (`MISSION.md`, `TECH.md`, `ROADMAP.md`) | ✅ Complete |
| `scripts/test`, `scripts/hooks` | ✅ Phase 1 |
| Application code | ⏳ Phases 2–7 |

Check [`SPECS/ROADMAP.md`](SPECS/ROADMAP.md) for the live build order.

## How it works

A hub-and-spoke pipeline built on Google ADK. The **Interviewer** is the
orchestrator; the others are specialists it delegates to.

| # | Stage | Model | What it does |
| --- | --- | --- | --- |
| 1 | **Bouncer** | Gemini 3.1 Flash Lite (vision) | Confirms the image contains a human. Cars, pets, and food get a cheeky rejection, and the run resets. |
| 2 | **Interviewer** *(orchestrator)* | Gemini 3.1 Flash Lite | Asks 5–7 questions, one per turn, and builds a behavioural dossier keyed by `chat_id`. Also suggests an animal. |
| 3 | **Converter** | Gemini 3.1 Flash Image | Fuses the original photo and the dossier into a hybrid animal portrait, sent straight to the chat. |
| 4 | **Scripter** | Gemini 3.1 Flash Lite | Writes one dramatic 60–90 word nature-documentary paragraph from the dossier. |
| 5 | **Narrator** | `gemini-3.1-flash-tts-preview` | Renders that paragraph to an OGG/MP3 voice note. |

**The Narrator is not an agent** — TTS is an execution tool. The orchestrator
simply forwards the Scripter's text to the Gemini TTS endpoint.

Transport is Telegram **long polling** (`getUpdates`). No webhooks, no public
URL, no tunneling tools. Session state is held **in memory**, keyed by
`chat_id`, and is purged by `/start` or `/restart` without restarting the
process.

## Requirements

- Python 3.11+
- `git`
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A [Google Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
# 1. Clone
git clone https://github.com/jirayu-codes/telegram-documentaries.git
cd telegram-documentaries

# 2. Create your local environment file
cp .env.example .env

# 3. Fill in your keys (see the table below)
$EDITOR .env
```

`.env` is gitignored and must never be committed. `.env.example` carries
placeholders only.

> Dependency installation and the run command land with **Phase 1** of the
> roadmap.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Auth token for the Telegram Bot API. Issued by @BotFather. |
| `GEMINI_API_KEY` | Yes | Google AI Studio key used for every Gemini call (vision, interview, image, TTS). |

Both are read from `.env` at startup. Never hardcode them — this is a
non-negotiable in [`SPECS/MISSION.md`](SPECS/MISSION.md).

## Development scripts

[`SPECS/TECH.md`](SPECS/TECH.md) names two scripts as the **ground truth** for
tests, lint, and type checks. Never bypass them with ad-hoc `pytest`, `ruff`,
or `mypy` calls.

| Script | Runs | Purpose |
| --- | --- | --- |
| `scripts/test` | pytest | Run the test suite. |
| `scripts/hooks` | pytest + ruff + ruff-format + mypy + gitleaks | The full pre-commit suite. |

⚠️ **Neither script exists yet** — both are created in Phase 1 (Repository &
gateway). Until then there is nothing to run.

## Testing philosophy

- **Red/Green TDD.** Tests are written before code, and must fail before they
  pass.
- Tests live in `tests/`, mirroring the source layout one file per module.
  - `tests/unit/` — pure logic (state machine, boundary contracts, parsers),
    no network access.
  - `tests/integration/` — module wiring with Telegram and Gemini faked at
    their boundary contracts.
- The suite **never makes live network calls**.

## Project structure

```
telegram-documentaries/
├── SPECS/                  # The constitution — single source of truth
│   ├── MISSION.md          # What the product is; in/out of scope
│   ├── TECH.md             # Stack, architecture, policies
│   └── ROADMAP.md          # Ordered build plan
├── .env.example            # Placeholder secrets (real .env is gitignored)
├── .guides/                # Guide illustration assets
├── applet_prompts.md       # Prompts used to generate the guide applets
└── telegram-arch.html      # Polling vs. webhooks guide page
```

## Specifications

Development follows **Spec-Driven Development**. Nothing gets built without a
spec.

- **[`SPECS/MISSION.md`](SPECS/MISSION.md)** — the product contract: what the
  bot does, what it explicitly will *not* do, and how we know it works.
- **[`SPECS/TECH.md`](SPECS/TECH.md)** — the technical contract: stack,
  architecture, the 8-phase state machine, boundary contracts, logging and
  error policy, testing rules.
- **[`SPECS/ROADMAP.md`](SPECS/ROADMAP.md)** — the ordered plan. Seven phases,
  each with acceptance criteria.

Individual features live in `SPECS/<YYYY-MM-DD>-<feature-name>/` as
`requirements.md`, `plan.md`, and `validation.md`.

## Out of scope

The constitution deliberately excludes, among other things: video output,
background music, persistence across restarts, group chats, multiple photos,
sharing to other chats, voice-message input, a web dashboard, and monetisation.
See the full list in [`SPECS/MISSION.md`](SPECS/MISSION.md).

## Tooling prerequisites

- **uv**: install via `pip install uv`. Verify with `uv --version`.
- **gitleaks**: install v8.30.1 into your PATH (e.g. `~/bin`):

```bash
curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz -o /tmp/gitleaks.tar.gz
tar -xzf /tmp/gitleaks.tar.gz -C /tmp gitleaks
mkdir -p "$HOME/bin"
install -m 0755 /tmp/gitleaks "$HOME/bin/gitleaks"
gitleaks version  # 8.30.1
```

Then `uv sync`.
