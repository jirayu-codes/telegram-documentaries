from __future__ import annotations

import os
from typing import Any

from . import settings

TEXT_MODEL = "gemini-3.1-flash-lite"
IMAGE_MODEL = "gemini-3.1-flash-image"
TTS_MODEL = "gemini-3.1-flash-tts-preview"


def _ensure_api_key() -> None:
    try:
        s = settings.load_settings()
        os.environ.setdefault("GOOGLE_API_KEY", s.gemini_api_key)
        os.environ.setdefault("GEMINI_API_KEY", s.gemini_api_key)
    except Exception:
        pass


def load_client() -> Any:
    _ensure_api_key()
    from google import genai

    try:
        s = settings.load_settings()
        return genai.Client(api_key=s.gemini_api_key)
    except Exception:
        return genai.Client()


def _user_content(parts: list[Any]) -> Any:
    from google.genai import types

    return types.Content(role="user", parts=parts)


def generate_text(
    prompt: str,
    *,
    model: str = TEXT_MODEL,
    image: tuple[bytes, str] | None = None,
) -> str:
    from google.genai import types

    client = load_client()
    parts: list[Any] = []
    if image is not None:
        data, mime = image
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
    parts.append(types.Part(text=prompt))
    response = client.models.generate_content(
        model=model,
        contents=_user_content(parts),
    )
    return str(getattr(response, "text", "") or "")


def generate_image(prompt: str, image: tuple[bytes, str]) -> bytes:
    from google.genai import types

    client = load_client()
    data, mime = image
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=_user_content(
            [types.Part.from_bytes(data=data, mime_type=mime), types.Part(text=prompt)]
        ),
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if content is None:
            continue
        for part in getattr(content, "parts", None) or []:
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                return bytes(inline.data)
    return b""
