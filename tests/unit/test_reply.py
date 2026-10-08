from telegram_documentaries import reply


def test_handler_returns_hardcoded_hey_mate() -> None:
    assert reply.handle_text_message() == "hey mate!"


def test_handler_ignores_input() -> None:
    assert reply.handle_text_message("anything") == "hey mate!"
    assert reply.handle_text_message("") == "hey mate!"
    assert reply.handle_text_message("/start") == "hey mate!"
    assert reply.handle_text_message("x" * 10000) == "hey mate!"
