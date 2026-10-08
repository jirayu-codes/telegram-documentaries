from __future__ import annotations

from typing import Any, Protocol, cast


class GeminiImageConverter(Protocol):
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes: ...


class _GeminiImageImpl:
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes:
        try:
            import google.generativeai as genai

            from . import settings

            s = settings.load_settings()
            cast(Any, genai).configure(api_key=s.gemini_api_key)
            model = cast(Any, genai).GenerativeModel("gemini-3.1-flash-image")
            prompt = (
                "Create a colorful chameleon perched on a branch, "
                "holding a paintbrush, painting a portrait. "
                "Fuse likeness from photo with quirks/dossier: "
                f"{dossier}. "
                "Return only the image."
            )
            response = model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
            )
            for part in getattr(response, "candidates", []) or []:
                content = getattr(part, "content", None)
                if not content:
                    continue
                for p in getattr(content, "parts", []) or []:
                    if getattr(p, "inline_data", None):
                        return bytes(p.inline_data.data)
            for p in getattr(response, "parts", []) or []:
                if getattr(p, "inline_data", None):
                    return bytes(p.inline_data.data)
            return image_bytes
        except Exception:
            return image_bytes


_converter: GeminiImageConverter = _GeminiImageImpl()


def set_converter(c: GeminiImageConverter) -> None:
    global _converter
    _converter = c


def generate_hybrid(image_bytes: bytes, dossier: str) -> bytes:
    return _converter.generate_hybrid(image_bytes, dossier)
