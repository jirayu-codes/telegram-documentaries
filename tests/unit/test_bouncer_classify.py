from telegram_documentaries import bouncer
from telegram_documentaries.types import ClassificationResult


class FakeClassifier:
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        assert image_bytes == b"data"
        assert mime == "image/jpeg"
        return ClassificationResult(is_human=True, reason="Looks like a human")


def test_classify_returns_result() -> None:
    bouncer.set_classifier(FakeClassifier())
    res = bouncer.classify(b"data", "image/jpeg")
    assert res.is_human is True
