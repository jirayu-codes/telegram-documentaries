# Requirements — Repository & Gateway (Phase 1)

## Context

ROADMAP Phase 1: *Repository & gateway — project skeleton, `.env` loading,
`scripts/test` + `scripts/hooks` in place, long-polling loop that replies with a
hardcoded message.*

The repository is greenfield for code purposes. Present today:

- `SPECS/` constitution and `README.md`
- `.env` with live credentials (gitignored, mode `600`) and `.env.example`
- `.gitignore`, guide assets, OpenCode agent config

Absent today: `pyproject.toml`, `uv.lock`, `src/`, `tests/`, `scripts/`, and
any git pre-commit hook.

## Scope

1. **Project skeleton** — `pyproject.toml` on a `src/` layout, managed by `uv`,
   with a committed `uv.lock`.
2. **Secret loading** — `.env` parsed into a typed Pydantic `Settings` model
   that fails loudly when a variable is missing or malformed.
3. **Dev scripts** — `scripts/test` and `scripts/hooks` as the ground truth
   named in `SPECS/TECH.md`.
4. **Pre-commit hook** — a versioned git hook that runs `scripts/hooks`,
   auto-wired for every clone.
5. **Gateway** — a Telegram long-polling loop (`getUpdates`) that replies to
   every incoming text message with the hardcoded string `hey mate!`.
6. **Red/Green TDD** — tests written before implementation.
7. **Docs** — `README.md` and `SPECS/TECH.md` updated to match reality.

## Decisions

| # | Decision | Choice | Rationale |
| --- | --- | --- | --- |
| D1 | Telegram library | `python-telegram-bot` | Batteries-included long polling; we own almost no loop code. |
| D2 | Dependency tooling | `uv` + committed `uv.lock` | Fast, one-command sync; satisfies TECH.md's lockfile rule. |
| D3 | Hook wiring | Versioned `scripts/git-hooks/pre-commit` + `git config core.hooksPath` | Zero extra dependencies; a plain hook that delegates to `scripts/hooks`. |
| D4 | `scripts/hooks` toolset | pytest + ruff + **ruff-format** + mypy + **gitleaks** | User-directed expansion of TECH.md's original three. **TECH.md is amended to all five.** |
| D5 | Telegram edge contract | `python-telegram-bot`'s typed `Update` | PTB already parses and validates the raw JSON. Wrapping it again in bespoke Pydantic would duplicate a library boundary for no gain (YAGNI). Our own typed contracts begin where *our* data crosses *our* module edges. |
| D6 | `.env` contract | Pydantic `Settings` | This is a boundary we own, so it gets a real typed contract: both variables required, non-empty, token structurally `<app_id>:<secret>`. |
| D7 | Gemini | **No calls of any kind** | First Gemini call lands with the Bouncer (Phase 2). |
| D8 | Command handling | None — `/start`, `/restart`, and plain text all get `hey mate!` | Command-specific behaviour is Phase 7 scope. Branching here would be speculative. |
| D9 | gitleaks install | Binary to `/home/codio/bin` (first writable entry on `PATH`) | No trusted PyPI package exists (`gitleaks-py` is an unrelated stub). The binary is **not** committed; absence fails loudly with install instructions. |
| D10 | Session state | None | The state machine starts at Phase 2. No per-`chat_id` storage yet. |

## Contracts

### Input — Telegram update (untrusted, arbitrary)

- Source: Telegram Bot API over long polling. May be malformed, partial,
  unexpected in shape, or arrive out of order.
- `python-telegram-bot` performs the edge parse; handlers receive a typed
  `Update`.
- The handler must tolerate: missing `text`, empty text, non-text messages,
  very long text, unknown update types, and commands.

### Output — reply

- Exact literal `hey mate!`, sent to the originating chat.
- Send failures are logged loudly and do **not** crash the polling loop
  (conversation-path degradation per TECH.md).

### Configuration — `Settings`

| Field | Rule on failure |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Missing/empty → raise at startup. Must split into exactly two non-empty parts around `:`. |
| `GEMINI_API_KEY` | Missing/empty → raise at startup. |

Invalid configuration is **non-user-visible work**, so it fails loudly and
aborts rather than degrading.

### Logging

- Structured key/value records emitted through **decorators**, not inline in
  business logic.
- Must cover: startup (secrets redacted), polling loop started, update
  received (`chat_id`), reply sent, and any error.
- No secret value may ever appear in a log line.

## Out of scope (this feature)

- Any Gemini API call.
- The Bouncer and vision classification.
- Session state and state-machine phases.
- `/start` and `/restart` semantics.
- Photo, audio, or any non-text media handling.
- Backward compatibility — greenfield, there is nothing to be compatible with.

## Non-functional

- `scripts/hooks` runs all five tools and exits non-zero on any failure, with a
  clear message naming the tool that failed.
- The pre-commit hook is committed and wired automatically; a fresh clone gets
  it after one documented command.
- Unit tests perform **no network I/O** (ROADMAP test philosophy).
- `.env` must remain untracked and gitleaks must report a clean scan.
