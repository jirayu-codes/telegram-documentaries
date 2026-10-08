from __future__ import annotations

import os
import tempfile
from typing import Any, Protocol, cast


class GeminiTTS(Protocol):
    def synthesize_voice(self, script: str) -> bytes: ...


class _GeminiTTSImpl:
    def synthesize_voice(self, script: str) -> bytes:
        try:
            from google import genai as _genai
            from google.genai import types as gtypes

            from . import settings

            s = settings.load_settings()
            genai = cast(Any, _genai)
            client = genai.Client(api_key=s.gemini_api_key)
            config = gtypes.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=gtypes.SpeechConfig(
                    voice_config=gtypes.VoiceConfig(
                        prebuilt_voice_config=gtypes.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                ),
            )
            response = client.models.generate_content(
                model="gemini-3.1-flash-tts-preview",
                contents=script,
                config=config,
            )
            return _extract_audio(response)
        except Exception:
            return _silent_wav()


def _extract_audio(response: Any) -> bytes:
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


def _silent_wav() -> bytes:
    try:
        import wave

        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(path, "w") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(b"\x00\x00" * 10)
        with open(path, "rb") as f:
            data = f.read()
        os.unlink(path)
        return data
    except Exception:
        return b""


_tts: GeminiTTS = _GeminiTTSImpl()


def set_tts(t: GeminiTTS) -> None:
    global _tts
    _tts = t


def synthesize_voice(script: str) -> bytes:
    return _tts.synthesize_voice(script)
