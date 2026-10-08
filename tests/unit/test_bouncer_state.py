from telegram_documentaries import state


def test_reset_clears_state() -> None:
    s = state.state
    s.get("123")["foo"] = "bar"
    s.reset("123")
    assert s.get("123") == {}
