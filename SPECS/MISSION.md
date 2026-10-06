# MISSION

## Vision

**The Telegram Documentaries** turns an ordinary portrait photo into a
narrated wildlife documentary about you. The user sends a photo to the bot; the
bot interviews them, renders them as a hybrid animal, and delivers a dramatic,
Attenborough-style one-paragraph narration as a Telegram voice note.

Transport is Telegram **long polling**. There is no web app, no public URL,
and no persistence beyond the running process.

## End-to-end user experience

1. `/start` — the bot greets the user and asks for a portrait photo.
2. The user sends a photo.
3. **The Bouncer** (Gemini 3.1 Flash Lite vision) confirms the image contains a
   human. Non-human images get a cheeky rejection and the run resets so another
   photo can be sent.
4. **The Interviewer** (Gemini 3.1 Flash Lite) — the orchestrator — asks 5–7
   questions, one per turn, and accumulates a behavioural dossier keyed by
   `chat_id`. It also suggests an animal.
5. **The Converter** (Gemini 3.1 Flash Image) fuses the original photo and the
   dossier into a hybrid animal portrait and sends it straight back to the chat.
6. **The Scripter** (Gemini 3.1 Flash Lite) writes one dramatic 60–90 word
   nature-documentary paragraph from the dossier.
7. **The Narrator** — not an agent — routes that text to
   `gemini-3.1-flash-tts-preview` and sends an OGG/MP3 voice note.
8. `/restart` — at any point, purges the run and its temporary media without
   restarting the process.

The narration persona is a **dramatic British naturalist**: hushed awe,
present tense, the user observed as a specimen in its habitat.

## In scope

- The eight-step experience above, exactly as written.
- Telegram long polling; in-memory session state keyed by `chat_id`.
- Secrets read from `.env`: `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`.

## Out of scope (YAGNI)

The project will **not** do any of the following. No feature spec may add an
item without amending this constitution first.

- **Video or animated output** — the product is a still image plus audio.
- **Background music or sound effects** — voice narration only.
- **Persisting sessions across restarts** — in-memory only; a restart
  legitimately forgets every conversation.
- **Group-chat support** — private 1:1 DMs only.
- **Multiple photos or a gallery** — one portrait per run; a new photo starts
  a fresh run.
- **Sharing or forwarding results** to other chats.
- **Voice-message input (speech-to-text)** — text and photos only.
- **A web dashboard or admin UI** — Telegram is the only interface.
- **Monetisation, ads, or user accounts.**

## Success criteria

- **Happy path:** photo → interview → hybrid portrait → narration → voice
  note, delivered end to end within a single chat.
- **Reset:** `/start` and `/restart` purge session state and temporary media
  while the process keeps running.
- **Robustness:** out-of-order input — text during photo intake, media mid-
  interview — is handled gracefully rather than crashing or corrupting state.

## Non-negotiables

- **Never leak another user's session.** State is strictly per-`chat_id`.
- **Never hardcode secrets.** `.env` only; `.env` stays in `.gitignore`.
- The out-of-scope list stays out of scope.
