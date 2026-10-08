# Validation — Repository & Gateway (Phase 1)

The feature can be merged when every check below passes. Checks are grouped so
they can be run through the dev scripts referenced in `README.md`.

## A. Automated gates (must all pass)

| # | Check | How | Expected |
| --- | --- | --- | --- |
| A1 | Test suite | `scripts/test` | Exit 0; suite green |
| A2 | Red/Green honoured | Inspect `plan.md` task 3.6 record | Tests were observed failing **before** implementation existed |
| A3 | Lint | inside `scripts/hooks` (`ruff check`) | No findings |
| A4 | Formatting | inside `scripts/hooks` (`ruff format --check`) | No files need reformatting |
| A5 | Types | inside `scripts/hooks` (`mypy`) | No errors |
| A6 | Secrets | inside `scripts/hooks` (`gitleaks detect`) | Clean scan |
| A7 | Hook fail-fast quality | Temporarily break lint, run `scripts/hooks` | Exits non-zero and **names the failing tool**; never a bare failure |

## B. Hook wiring

| # | Check | How | Expected |
| --- | --- | --- | --- |
| B1 | Hooks path configured | `git config core.hooksPath` | `scripts/git-hooks` |
| B2 | Hook is versioned | `git ls-files scripts/git-hooks/pre-commit` | Tracked |
| B3 | Hook actually fires | Stage a file with a deliberate lint error, `git commit` | Commit blocked; `scripts/hooks` output shown |
| B4 | Hook is the single path | `scripts/git-hooks/pre-commit` delegates to `scripts/hooks` | No duplicated tool invocations |

## C. Configuration & secrets

| # | Check | How | Expected |
| --- | --- | --- | --- |
| C1 | `.env` untracked | `git check-ignore -v .env` | Ignored by `.gitignore` |
| C2 | `.env` absent from history | `git log --all -- .env` | Empty |
| C3 | `.env.example` still placeholders | `cat .env.example` | No real credentials |
| C4 | Invalid config fails loud | Remove `GEMINI_API_KEY`, start gateway | Raises at startup with a clear message; does not half-start |
| C5 | No secret in logs | Start gateway, inspect logs | Token/key never printed |
| C6 | Lockfile present | `git ls-files uv.lock` | Tracked |

## D. Gateway behaviour (Step 3 — manual, on a real client)

| # | Check | Expected |
| --- | --- | --- |
| D1 | Start the process | Logs show configuration loaded (redacted) and the long-polling loop started |
| D2 | Send any text from a phone | Bot replies exactly `hey mate!` |
| D3 | Repeat several messages | Same reply every time, no drift |
| D4 | Send a command (`/start`) | Same `hey mate!` reply (D8 — no branching yet) |
| D5 | Send non-text (sticker/photo) | No crash; loop keeps running; loudly logged |
| D6 | Stop the process | Clean shutdown, no traceback |

## E. Spec reconciliation

| # | Check |
| --- | --- |
| E1 | Every scope item in `requirements.md` is implemented, or the difference is surfaced to the user |
| E2 | No out-of-scope work crept in (no Gemini calls, no session state, no media handling) |
| E3 | `README.md` matches reality — every documented command runs |
| E4 | `SPECS/TECH.md` amended to the five-tool `scripts/hooks` |
| E5 | `ROADMAP.md` Phase 1 marked complete **only after** A–E pass |
| E6 | Any spec amendment is approved by the user, not assumed |

## Merge blockers

A failure of **any** of A1–A7, B1–B4, C1–C3, C6, or E1–E4 blocks merge.
D1–D6 are manually observed and must be reported before merge, since they
cannot be automated without a live Telegram client.
