# Requirements — Interviewer (Phase 3)

## Context
ROADMAP Phase 3: Interviewer — sequential stateful Q&A (5–7 questions, one per turn), dossier summary, suggested animal. The Bouncer approves humans; now we must interview them turn by turn, storing history per `chat_id`.

## Scope
1. Sequential Qs: ask 5–7 questions one at a time, waiting for user reply each turn. No dumping all questions at once.
2. State machine extension: track phase (AWAITING_ANSWER_n, DONE_INTERVIEW, etc), question index, history (question + answer), dossier text, suggested_animal. Per `chat_id`, in-memory only.
3. Model: gemini-3.1-flash-lite. Generate questions in investigative/playful/slightly eccentric tone.
4. After collecting all answers (5–7), synthesize a clean behavioral dossier + suggest an animal. Output handoff summary (text) for next stage.
5. Turn-taking: don’t advance until user replies; handle out-of-order gracefully per existing rules.
6. Integrate with existing gateway/state (reuse state module). Don’t break text-only or bouncer flows.

## Decisions
- Extend state schema to include interview fields (question_count: 5-7, chosen at start of interview).
- Generate first question after bouncer approves human (transition appropriately).
- Dossier must include concrete quirks (sleep cycles, territory marking, favorite forage etc) as implied, and also `suggested_animal` string.
- Output handoff format: structured text block containing dossier and "Suggested animal: ..."

## Contracts
- State per chat_id, versioned conceptually. Reset on /restart (already supported via state.reset).
- All external calls behind interface (mock in tests).
- Structured logging.

## Out of scope
- Converter/Scripter/Narrator (4+). Just produce handoff.
- Persistence across restarts.

## Non-functional
- No network in tests; Red/Green TDD.
- Use scripts/test and scripts/hooks.
