from __future__ import annotations

from typing import Protocol

from . import gemini

_PROMPT = (
    "Create a vivid, colourful hybrid portrait: blend the human subject in the "
    "photo with the animal archetype that best matches their personality. "
    "Render it as a playful wildlife-documentary still — the creature in a lush "
    "habitat, mid-activity, matching the subject's quirks. Keep a recognisable "
    "echo of the person's face and features. Do not add text or watermarks."
)


class GeminiImageConverter(Protocol):
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes: ...


class _GeminiImageImpl:
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes:
        prompt = f"{_PROMPT} Personality dossier: {dossier}"
        try:
            result = gemini.generate_image(prompt, (image_bytes, "image/jpeg"))
        except Exception:
            return b""
        return result


_converter: GeminiImageConverter = _GeminiImageImpl()


def set_converter(c: GeminiImageConverter) -> None:
    global _converter
    _converter = c


def generate_hybrid(image_bytes: bytes, dossier: str) -> bytes:
    return _converter.generate_hybrid(image_bytes, dossier)
