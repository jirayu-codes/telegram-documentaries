from __future__ import annotations

import os
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

    def purge(self, chat_id: int | str) -> None:
        """Cancel the session and delete any ephemeral files on disk."""
        key = str(chat_id)
        data = self._store.get(key, {})
        for field, value in data.items():
            if field.endswith("_path") and isinstance(value, str):
                _safe_unlink(value)
        self._store[key] = {}

    def clear_all(self) -> None:
        for key in list(self._store):
            self.purge(key)
        self._store.clear()


def _safe_unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        return


state = State()
