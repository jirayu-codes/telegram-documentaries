from __future__ import annotations

import json
from typing import Any, Protocol

from . import gemini
from .types import ClassificationResult

TEXT_MODEL = "gemini-3.1-flash-lite"


class GeminiClassifier(Protocol):
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult: ...


class _GeminiImpl:
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        prompt = (
            "You are a strict, slightly theatrical bouncer at the door of a "
            "wildlife documentary. Decide whether the image contains a "
            "discernible human face or body. Respond ONLY as JSON: "
            '{"is_human": true|false, "reason": "<brief cheeky explanation>"}'
        )
        try:
            text = gemini.generate_text(
                prompt,
                model=TEXT_MODEL,
                image=(image_bytes, mime),
            )
            data: dict[str, Any] = json.loads(_strip_code_fence(text).strip())
            return ClassificationResult(
                is_human=bool(data.get("is_human")),
                reason=str(data.get("reason", "")),
            )
        except Exception:
            return ClassificationResult(
                is_human=False,
                reason="Security camera's gone fuzzy — can't confirm a human.",
            )


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    return cleaned


_classifier: GeminiClassifier = _GeminiImpl()


def set_classifier(c: GeminiClassifier) -> None:
    global _classifier
    _classifier = c


def classify(image_bytes: bytes, mime: str) -> ClassificationResult:
    return _classifier.classify(image_bytes, mime)
