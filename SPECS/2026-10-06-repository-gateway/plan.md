# Plan — Repository & Gateway (Phase 1)

Red/Green TDD: task group 3 (tests) must be written and observed **failing**
before task group 4 (implementation) exists.

Whenever a check is needed — tests, lint, format, types, secrets — run it
through the dev scripts in `scripts/` referenced by `README.md`. Do not invoke
`pytest`, `ruff`, `mypy`, or `gitleaks` directly.

## 1. Toolchain & project skeleton

1.1. Install `uv` (PyPI package `uv`, official distribution channel).
1.2. Install gitleaks `v8.30.1` from the GitHub release asset
     `gitleaks_8.30.1_linux_x64.tar.gz` into `/home/codio/bin` (first writable
     entry on `PATH`). Verify with `gitleaks version`.
1.3. Create `pyproject.toml` on a `src/` layout with runtime dependencies
     (`python-telegram-bot`, `pydantic`, `python-dotenv`) and dev
     dependencies (`pytest`, `ruff`, `mypy`).
1.4. Run `uv lock` and commit `uv.lock`.
1.5. Extend `.gitignore` for `.venv/`, `.ruff_cache/`, `.mypy_cache/`,
     `.pytest_cache/`. Confirm `.env` stays ignored.

## 2. Dev scripts & pre-commit hook

2.1. Create `scripts/test` — runs the suite via `uv run pytest`.
2.2. Create `scripts/hooks` — runs, in order, failing fast and naming the
     offending tool: `pytest`, `ruff check`, `ruff format --check`, `mypy`,
     `gitleaks detect`.
2.3. Create `scripts/git-hooks/pre-commit` which delegates to `scripts/hooks`.
2.4. Make all three executable; wire with
     `git config core.hooksPath scripts/git-hooks`.
2.5. Run `scripts/hooks` — expected to fail here (no tests yet). Confirm the
     wiring and failure messages are correct rather than silently passing.

## 3. Red — tests before implementation

3.1. `tests/unit/test_settings.py` — missing, empty, and malformed
     `TELEGRAM_BOT_TOKEN` / `GEMINI_API_KEY` each raise; valid values load.
3.2. `tests/unit/test_reply.py` — the handler returns exactly `hey mate!` for
     arbitrary text.
3.3. `tests/unit/test_reply.py` — the handler never raises on empty text, no
     text, a command, or oversized input.
3.4. `tests/unit/test_logging.py` — the logging decorator emits structured
     records and preserves the wrapped result and any exception.
3.5. `tests/integration/test_gateway.py` — handler wiring with a faked bot;
     **no network**.
3.6. Run `scripts/test` and observe it **FAIL**. Record the failure output.

## 4. Green — implementation

4.1. `src/.../settings.py` — Pydantic `Settings` loaded from `.env`; raises
     loudly on invalid configuration.
4.2. `src/.../logging.py` — structured logging decorators.
4.3. `src/.../reply.py` — the hardcoded reply handler.
4.4. `src/.../gateway.py` — `python-telegram-bot` Application, long polling,
     startup logging with secrets redacted, conversation-path error
     degradation.
4.5. Run `scripts/test` until **PASS**.
4.6. Run `scripts/hooks` until **PASS** (all five tools).

## 5. Documentation & constitution amendment

5.1. `README.md` — replace the "pre-implementation" warnings with real setup
     (`uv sync`), the `scripts/` table, and the gitleaks install step.
5.2. `SPECS/TECH.md` — amend `scripts/hooks` to the five tools
     (pytest + ruff + ruff-format + mypy + gitleaks) and name `scripts/`
     conventions.
5.3. Do **not** mark Phase 1 complete in `ROADMAP.md`; that happens only after
     validation is verified.

## 6. Validation

6.1. `scripts/test` passes.
6.2. `scripts/hooks` passes all five tools.
6.3. `git check-ignore` confirms `.env` untracked; working tree carries no
     secrets.
6.4. Launch the gateway, confirm the polling-loop log line, and receive
     `hey mate!` on a real Telegram client (Step 3).
6.5. Reconcile implementation against `requirements.md` and the constitution;
     surface every difference to the user and update the specs only with
     approval.
