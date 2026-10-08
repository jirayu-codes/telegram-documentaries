from __future__ import annotations

from typing import Any, Protocol, cast

from .state import state


class GeminiInterviewer(Protocol):
    def generate_question(self, history: list[dict[str, str]]) -> str: ...
    def synthesize(self, history: list[dict[str, str]]) -> tuple[str, str]: ...


class _GeminiImpl:
    def generate_question(self, history: list[dict[str, str]]) -> str:
        try:
            import google.generativeai as genai

            from . import settings

            s = settings.load_settings()
            cast(Any, genai).configure(api_key=s.gemini_api_key)
            model = cast(Any, genai).GenerativeModel("gemini-3.1-flash-lite")
            hist = str(history)
            intro = "You are an investigative, playful, documentary researcher. "
            q_req = "Ask ONE sharp question (5-7 words). "
            h_req = "History: "
            end = ". Return only the question text."
            prompt = intro + q_req + h_req + hist + end
            response = model.generate_content([prompt])
            text = (
                getattr(response, "text", "")
                or "Tell me one quirky thing about your day."
            )
            return text.strip()
        except Exception:
            return "Tell me one quirky thing about your day."

    def synthesize(self, history: list[dict[str, str]]) -> tuple[str, str]:
        try:
            import google.generativeai as genai

            from . import settings

            s = settings.load_settings()
            cast(Any, genai).configure(api_key=s.gemini_api_key)
            model = cast(Any, genai).GenerativeModel("gemini-3.1-flash-lite")
            prompt = (
                "Synthesize a clean behavioral dossier from history. "
                "Also suggest an animal. "
                f"History: {history}. Return JSON: "
                '{"dossier": "...", "suggested_animal": "..."}'
            )
            response = model.generate_content([prompt])
            text = getattr(response, "text", "") or (
                '{"dossier": "curious subject", "suggested_animal": "fox"}'
            )
            import json

            data: dict[str, Any] = json.loads(text.strip())
            dossier = str(data.get("dossier", "curious"))
            animal = str(data.get("suggested_animal", "fox"))
            return dossier, animal
        except Exception:
            return "curious subject", "fox"


_interviewer: GeminiInterviewer = _GeminiImpl()


def set_interviewer(i: GeminiInterviewer) -> None:
    global _interviewer
    _interviewer = i


def start_interview(chat_id: int | str, question_count: int = 5) -> str:
    st = state.get(chat_id)
    qcount = int(question_count)
    if qcount < 5:
        qcount = 5
    if qcount > 7:
        qcount = 7
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
    qcount = int(iv.get("question_count", 5))
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
