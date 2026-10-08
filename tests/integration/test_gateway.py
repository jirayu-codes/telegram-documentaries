from telegram_documentaries import gateway


def test_gateway_has_main() -> None:
    assert callable(gateway.main)
