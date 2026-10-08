from __future__ import annotations

from typing import Any, Protocol, cast


class GeminiScripter(Protocol):
    def generate_script(self, summary: str) -> str: ...


class _GeminiScripterImpl:
    def generate_script(self, summary: str) -> str:
        try:
            import google.generativeai as genai

            from . import settings

            s = settings.load_settings()
            cast(Any, genai).configure(api_key=s.gemini_api_key)
            model = cast(Any, genai).GenerativeModel("gemini-3.1-flash-lite")
            prompt = (
                "Adopt persona of a dramatic British wildlife documentary narrator. "
                "Frame quirks, bedtime, and snacking as funny animal behaviours, "
                "like a nature documentary about humans. "
                f"Subject summary: {summary}. "
                "Output: exactly one paragraph (max 90 words), no markdown."
            )
            response = model.generate_content([prompt])
            text = getattr(response, "text", "") or ""
            return text.strip()
        except Exception:
            return "Ah, behold the rare specimen... peculiar habits indeed."

    def synthesize(self, summary: str) -> str:
        return self.generate_script(summary)


_scripter: GeminiScripter = _GeminiScripterImpl()


def set_scripter(sc: GeminiScripter) -> None:
    global _scripter
    _scripter = sc


def generate_script(summary: str) -> str:
    return _scripter.generate_script(summary)
