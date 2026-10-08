from __future__ import annotations

import json
from typing import Any, Protocol

from . import gemini
from .state import state

MIN_QUESTIONS = 5
MAX_QUESTIONS = 7

_PERSONA = (
    "You are an investigative, playful, slightly eccentric documentary "
    "researcher studying a human specimen before filming."
)


class GeminiInterviewer(Protocol):
    def generate_question(self, history: list[dict[str, str]]) -> str: ...
    def synthesize(self, history: list[dict[str, str]]) -> tuple[str, str]: ...


class _GeminiImpl:
    def generate_question(self, history: list[dict[str, str]]) -> str:
        prompt = (
            f"{_PERSONA} Ask exactly ONE short question (5-7 words) about the "
            "subject's habits, bedtime, or snacking. Return ONLY the question "
            f"text, no quotes or numbering. Conversation so far: {history}"
        )
        try:
            text = gemini.generate_text(prompt)
            text = text.strip().strip('"').strip()
            return text or "What do you snack on at midnight?"
        except Exception:
            return "What do you snack on at midnight?"

    def synthesize(self, history: list[dict[str, str]]) -> tuple[str, str]:
        prompt = (
            f"{_PERSONA} Synthesize a rich behavioural dossier from the "
            "conversation, then suggest the animal that best matches these "
            "quirks. Return ONLY JSON: "
            '{"dossier": "...", "suggested_animal": "..."}. '
            f"Conversation: {history}"
        )
        try:
            text = gemini.generate_text(prompt)
            data: dict[str, Any] = json.loads(_strip_code_fence(text).strip())
            dossier = str(data.get("dossier", "A deeply curious specimen."))
            animal = str(data.get("suggested_animal", "fox"))
            return dossier, animal
        except Exception:
            return "A deeply curious specimen with mysterious habits.", "fox"


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    return cleaned


_interviewer: GeminiInterviewer = _GeminiImpl()


def set_interviewer(i: GeminiInterviewer) -> None:
    global _interviewer
    _interviewer = i


def start_interview(chat_id: int | str, question_count: int = MIN_QUESTIONS) -> str:
    st = state.get(chat_id)
    qcount = int(question_count)
    if qcount < MIN_QUESTIONS:
        qcount = MIN_QUESTIONS
    if qcount > MAX_QUESTIONS:
        qcount = MAX_QUESTIONS
    q = _interviewer.generate_question([])
    st["interview"] = {
        "phase": "AWAITING_ANSWER_1",
        "history": [],
        "dossier": "",
        "suggested_animal": "",
        "question_count": qcount,
        "current_question": q,
        "answers_received": 0,
        "questions_generated": 1,
    }
    return q


def handle_answer(chat_id: int | str, answer: str) -> str | None:
    st = state.get(chat_id)
    iv = st.get("interview")
    if not iv:
        return None
    q = iv.get("current_question", "")
    hist = list(iv.get("history", []))
    hist.append({"question": q, "answer": answer})
    iv["history"] = hist
    answers_received = int(iv.get("answers_received", 0)) + 1
    iv["answers_received"] = answers_received
    qcount = int(iv.get("question_count", MIN_QUESTIONS))
    if answers_received >= qcount:
        dossier, animal = _interviewer.synthesize(hist)
        iv["dossier"] = dossier
        iv["suggested_animal"] = animal
        iv["phase"] = "DONE_INTERVIEW"
        return f"Dossier: {dossier}\nSuggested animal: {animal}"
    nq = _interviewer.generate_question(hist)
    iv["phase"] = f"AWAITING_ANSWER_{answers_received + 1}"
    iv["current_question"] = nq
    iv["questions_generated"] = int(iv.get("questions_generated", 1)) + 1
    return nq
