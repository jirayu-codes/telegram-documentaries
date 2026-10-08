from __future__ import annotations

from typing import Any, Protocol, cast

from .types import ClassificationResult


class GeminiClassifier(Protocol):
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult: ...


class _GeminiImpl:
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        try:
            import google.generativeai as genai

            from . import settings

            s = settings.load_settings()
            cast(Any, genai).configure(api_key=s.gemini_api_key)
            model = cast(Any, genai).GenerativeModel("gemini-3.1-flash-lite")
            prompt = (
                "You are a strict bouncer. Classify if the image contains a "
                "discernible human face or body. Respond only as JSON: "
                '{"is_human": true|false, "reason": "<brief cheeky explanation>"}'
            )
            response = model.generate_content(
                [prompt, {"mime_type": mime, "data": image_bytes}]
            )
            text = getattr(response, "text", "") or ""
            import json

            data: dict[str, Any] = json.loads(text.strip())
            return ClassificationResult(
                is_human=bool(data.get("is_human")),
                reason=str(data.get("reason", "")),
            )
        except Exception:
            return ClassificationResult(
                is_human=False, reason="Looks suspicious — not clearly human."
            )


_classifier: GeminiClassifier = _GeminiImpl()


def set_classifier(c: GeminiClassifier) -> None:
    global _classifier
    _classifier = c


def classify(image_bytes: bytes, mime: str) -> ClassificationResult:
    return _classifier.classify(image_bytes, mime)
