from __future__ import annotations

from telegram_documentaries import interviewer


class FakeInt:
    def __init__(self) -> None:
        self.calls = 0

    def generate_question(self, history: list[dict[str, str]]) -> str:
        _ = history
        self.calls += 1
        return f"Q{self.calls}"

    def synthesize(self, history: list[dict[str, str]]) -> tuple[str, str]:
        _ = history
        return "dossier text", "fox"


def test_interview_flow() -> None:
    interviewer.set_interviewer(FakeInt())
    q = interviewer.start_interview("1", question_count=5)
    assert q == "Q1"
    r1 = interviewer.handle_answer("1", "A")
    assert r1 == "Q2"
    r2 = interviewer.handle_answer("1", "B")
    assert r2 == "Q3"
    r3 = interviewer.handle_answer("1", "C")
    assert r3 == "Q4"
    r4 = interviewer.handle_answer("1", "D")
    assert r4 == "Q5"
    r5 = interviewer.handle_answer("1", "E")
    assert "Dossier:" in str(r5) and "fox" in str(r5)
