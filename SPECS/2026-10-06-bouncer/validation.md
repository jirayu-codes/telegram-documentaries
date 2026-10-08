# Validation — Bouncer (Phase 2)

## A. Automated
- A1 `scripts/test` passes
- A2 Red→Green observed (tests failed before impl)
- A3 `scripts/hooks` all 5 pass

## B. Behavior (live manual)
- B1 Negative: send photo of coffee mug/landscape → cheeky rejection, explains why, does not proceed to interview; state reset
- B2 Positive: send clear photo of person → approved, triggers pipeline confirmation step (matches success criteria)
- B3 Text still works (regression: `hey mate!`)
- B4 Non-text media (sticker) handled gracefully
- B5 Logs structured, no secrets

## C. Spec reconciliation
- C1 All scope satisfied or differences surfaced
- C2 No out-of-scope creep
- C3 Constitution respected
