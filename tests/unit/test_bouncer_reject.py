from telegram_documentaries import bouncer
from telegram_documentaries.types import ClassificationResult


class FakeReject:
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        return ClassificationResult(is_human=False, reason="That’s a toaster, mate.")


def test_reject_message_includes_reason() -> None:
    bouncer.set_classifier(FakeReject())
    res = bouncer.classify(b"x", "image/jpeg")
    assert res.is_human is False
    assert "toaster" in res.reason
