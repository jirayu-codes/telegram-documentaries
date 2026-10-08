# Requirements — Resilience (Phase 7)

## Scope
Make the bot recoverable without a process restart, and harden the phase
transitions against out-of-order / unexpected input.

## Explicit reset (`/start` and `/restart`)
A single routine must run for the requesting `chat_id`, performing three actions:

1. **Cancel active sessions** — terminate any running interview loop or waiting
   state so no further turns are expected.
2. **Purge ephemeral assets** — delete temporary media on disk (original photo,
   converted image, generated OGG/MP3 voice files). In-memory bytes are dropped
   with the session.
3. **Re-initialise agent memory** — clear history buffers and reset trackers
   back to the greeting stage (empty session state).

Implementation: `state.purge(chat_id)` walks every `*_path` field in the session,
`os.unlink`s each file, then clears the session. `handlers.handle_restart` is
wired to `CommandHandler(["start", "restart"], ...)`.

## Defensive guards (bonus)
- **Photo during the interview stage** → ask the user to finish the current
  question with text, or send `/restart`.
- **Text before a photo (Bouncer stage)** → instruct the user to upload a clear
  portrait photo.
- **API failures (Gemini vision/TTS)** → existing try/except boundaries; the
  handlers catch unexpected errors, notify the user, and offer `/restart`
  instead of crashing the polling loop.

## Acceptance criteria
- Sending `/restart` mid-interview clears state and temp files, and the next
  photo starts a fresh run — with no server reboot.
- A second full run (photo → interview → portrait → script → voice) succeeds in
  the same process.
- `scripts/test` and `scripts/hooks` pass.
