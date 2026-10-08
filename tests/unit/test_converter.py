from telegram_documentaries import converter


class FakeConv:
    def generate_hybrid(self, image_bytes: bytes, dossier: str) -> bytes:
        return b"IMG:" + image_bytes + dossier.encode("utf-8")[:10]


def test_generate_hybrid() -> None:
    converter.set_converter(FakeConv())
    out = converter.generate_hybrid(b"abc", "quirky fox")
    assert out.startswith(b"IMG:")
