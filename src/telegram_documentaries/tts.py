from __future__ import annotations

import os
import tempfile
from typing import Protocol


class GeminiTTS(Protocol):
    def synthesize_voice(self, script: str) -> bytes: ...


class _GeminiTTSImpl:
    def synthesize_voice(self, script: str) -> bytes:
        try:
            from google import genai

            from . import settings

            s = settings.load_settings()
            client = genai.Client(api_key=s.gemini_api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=script,
                config={
                    "response_modalities": ["AUDIO"],
                    "audio_config": {
                        "audio_encoding": "LINEAR16",
                        "voice_config": {
                            "prebuilt_voice_config": {"voice_name": "Kore"}
                        },
                    },
                },
            )
            # Extract audio data
            data = None
            if response.candidates:
                parts = response.candidates[0].content.parts
                for p in parts:
                    if hasattr(p, "inline_data") and p.inline_data is not None:
                        data = p.inline_data.data
                        break
            if data is None:
                return b""
            return bytes(data)
        except Exception:
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
                    b = f.read()
                try:
                    os.unlink(path)
                except Exception:
                    pass
                return b
            except Exception:
                return b""


_tts: GeminiTTS = _GeminiTTSImpl()


def set_tts(t: GeminiTTS) -> None:
    global _tts
    _tts = t


def synthesize_voice(script: str) -> bytes:
    return _tts.synthesize_voice(script)
