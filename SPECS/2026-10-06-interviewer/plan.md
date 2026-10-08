# Plan — Interviewer (Phase 3)

1. Extend state (interview phase, q_index, history list, dossier, suggested_animal, question_count).
2. Red tests: interview flow (one question at a time), completion produces dossier+animal, state per chat_id, reset works.
3. Green: interviewer module (Gemini or scripted? but must use gemini-3.1-flash-lite to generate questions and synthesize; mock in tests). Also interface.
4. Wire into flow: after bouncer approves human photo, start interview (ask first question).
5. Handle user answers: store answer, advance, maybe ask next or synthesize.
6. Tests + hooks pass.

Also update gateway/handlers minimally. No network in tests.
