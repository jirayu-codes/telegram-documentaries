from _pytest.logging import LogCaptureFixture

from telegram_documentaries import logging as tlog


def test_structured_logging_decorator_preserves_result_and_emits(
    caplog: LogCaptureFixture,
) -> None:
    @tlog.log_call("test.op")
    def op(x: int) -> int:
        return x + 1

    with caplog.at_level("INFO"):
        assert op(2) == 3
    records = caplog.records
    messages = [r.getMessage() for r in records]
    assert any("event=test.op" in m for m in messages)
