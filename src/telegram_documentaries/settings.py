from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    telegram_bot_token: str
    gemini_api_key: str


def load_settings(env_file: Path | None = None) -> Settings:
    if env_file is None:
        load_dotenv()
    else:
        load_dotenv(dotenv_path=env_file, override=True)

    token = os.getenv("TELEGRAM_BOT_TOKEN") or ""
    key = os.getenv("GEMINI_API_KEY") or ""

    if token == "":
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
    if key == "":
        raise RuntimeError("Missing GEMINI_API_KEY")
    if ":" not in token:
        raise RuntimeError("Invalid TELEGRAM_BOT_TOKEN format")
    parts = token.split(":", 1)
    if parts[0] == "" or parts[1] == "":
        raise RuntimeError("Invalid TELEGRAM_BOT_TOKEN format")

    return Settings(telegram_bot_token=token, gemini_api_key=key)
