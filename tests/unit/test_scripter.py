from telegram_documentaries import scripter


class FakeScr:
    def generate_script(self, summary: str) -> str:
        return f"Ah, behold the rare {summary}... most peculiar!"


def test_generate_script() -> None:
    scripter.set_scripter(FakeScr())
    out = scripter.generate_script("subject")
    assert "subject" in out
