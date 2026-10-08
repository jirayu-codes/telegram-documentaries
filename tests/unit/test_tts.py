from telegram_documentaries import tts


class FakeTTS:
    def synthesize_voice(self, script: str) -> bytes:
        return b"WAV" + script.encode("utf-8")[:5]


def test_tts() -> None:
    tts.set_tts(FakeTTS())
    out = tts.synthesize_voice("hello")
    assert out.startswith(b"WAV")
