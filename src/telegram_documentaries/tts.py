from __future__ import annotations

import io
import os
import tempfile
import wave
from typing import Any, Protocol, cast

TTS_MODEL = "gemini-3.1-flash-tts-preview"
VOICE_NAME = "Charon"  # deep male voice
STYLE = "Read in a deep male voice with a posh British accent, like a dramatic narrator"


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
                            voice_name=VOICE_NAME
                        )
                    )
                ),
            )
            response = client.models.generate_content(
                model=TTS_MODEL,
                contents=f"{STYLE}: {script}",
                config=config,
            )
            pcm = _extract_audio(response)
            if not pcm:
                return b""
            return _encode_ogg(pcm)
        except Exception:
            return _silent_ogg()


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


def _pcm_to_wav_bytes(pcm: bytes, rate: int = 24000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


def _encode_ogg(pcm: bytes) -> bytes:
    import soundfile as sf  # type: ignore[import-untyped]

    if pcm[:4] == b"RIFF":
        wav_bytes = pcm
    else:
        wav_bytes = _pcm_to_wav_bytes(pcm)
    data, rate = sf.read(io.BytesIO(wav_bytes), dtype="int16")
    out = io.BytesIO()
    sf.write(out, data, rate, format="OGG", subtype="OPUS")
    return out.getvalue()


def _silent_ogg(seconds: float = 0.25, rate: int = 24000) -> bytes:
    try:
        import numpy as np
        import soundfile as sf

        frames = int(seconds * rate)
        silence = np.zeros(frames, dtype="int16")
        out = io.BytesIO()
        sf.write(out, silence, rate, format="OGG", subtype="OPUS")
        return out.getvalue()
    except Exception:
        return b""


_tts: GeminiTTS = _GeminiTTSImpl()


def set_tts(t: GeminiTTS) -> None:
    global _tts
    _tts = t


def synthesize_voice(script: str) -> bytes:
    return _tts.synthesize_voice(script)


def write_temp_ogg(audio: bytes) -> str:
    fd, path = tempfile.mkstemp(suffix=".ogg")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(audio)
    return path
