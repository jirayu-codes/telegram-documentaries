from __future__ import annotations

from typing import Any


class State:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, chat_id: int | str) -> dict[str, Any]:
        key = str(chat_id)
        if key not in self._store:
            self._store[key] = {}
        return self._store[key]

    def reset(self, chat_id: int | str) -> None:
        self._store[str(chat_id)] = {}

    def clear_all(self) -> None:
        self._store.clear()


state = State()
