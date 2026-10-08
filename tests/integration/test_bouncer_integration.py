from telegram_documentaries import bouncer, handlers
from telegram_documentaries.types import ClassificationResult


class FakeClassifier:
    def classify(self, image_bytes: bytes, mime: str) -> ClassificationResult:
        return ClassificationResult(is_human=True, reason="ok")


def test_wiring_works() -> None:
    bouncer.set_classifier(FakeClassifier())
    assert callable(handlers.handle_photo)
