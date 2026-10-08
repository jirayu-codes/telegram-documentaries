from __future__ import annotations

from typing import Protocol

from . import gemini

_MAX_WORDS = 90

_SYSTEM = (
    "You are a revered, dramatic British wildlife documentary narrator "
    "(think David Attenborough). Observe the human subject as if it were a "
    "wild beast in its natural habitat. Frame its quirks, bedtime habits, and "
    "snacking patterns as remarkable animal behaviours, with hushed awe and "
    "gentle comedy. Output exactly ONE paragraph of 60-90 words, plain prose, "
    "no markdown, no headings, ready to be read aloud."
)


class GeminiScripter(Protocol):
    def generate_script(self, summary: str) -> str: ...


class _GeminiImpl:
    def generate_script(self, summary: str) -> str:
        prompt = f"{_SYSTEM} Subject dossier: {summary}"
        try:
            text = gemini.generate_text(prompt).strip()
            return _enforce_one_paragraph(text)
        except Exception:
            return (
                "And here, in the fading light, we find our subject — a "
                "remarkable specimen of quiet routines and questionable "
                "snacking, perfectly adapted to its peculiar little habitat."
            )


def _enforce_one_paragraph(text: str) -> str:
    collapsed = " ".join(text.split())
    words = collapsed.split(" ")
    if len(words) > _MAX_WORDS:
        collapsed = " ".join(words[:_MAX_WORDS]).rstrip(",;:") + "."
    return collapsed


_scripter: GeminiScripter = _GeminiImpl()


def set_scripter(sc: GeminiScripter) -> None:
    global _scripter
    _scripter = sc


def generate_script(summary: str) -> str:
    return _scripter.generate_script(summary)
