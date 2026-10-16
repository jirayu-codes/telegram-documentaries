from __future__ import annotations

import logging
from typing import Protocol

from . import gemini

LOGGER = logging.getLogger("telegram_documentaries")

_PROMPT = (
    "Blend this person with the animal that best matches their personality in "
    "a playful wildlife documentary still — colourful, cinematic, in a lush "
    "habitat, mid-activity, keeping a playful resemblance to the original "
    "face. Do not add text. Personality dossier: {dossier}"
)


class GeminiImageConverter(Protocol):
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes: ...


class _GeminiImageImpl:
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes:
        prompt = _PROMPT.format(dossier=dossier)
        try:
            result = gemini.generate_image(prompt, (image_bytes, "image/jpeg"))
        except Exception:
            LOGGER.exception("event=converter.error")
            return b""
        if not result:
            LOGGER.warning("event=converter.empty_image")
        return result


_converter: GeminiImageConverter = _GeminiImageImpl()


def set_converter(c: GeminiImageConverter) -> None:
    global _converter
    _converter = c


def generate_hybrid(image_bytes: bytes, dossier: str) -> bytes:
    return _converter.generate_hybrid(image_bytes, dossier)
