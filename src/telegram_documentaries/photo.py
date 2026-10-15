from __future__ import annotations

from typing import Any

from . import logging as tlog
from .types import PhotoPayload


@tlog.log_call("photo.download")
async def download_photo(
    bot: Any, file_id: str, chat_id: int | str
) -> PhotoPayload | None:
    try:
        file = await bot.get_file(file_id)
        bytes_data = await file.download_as_bytearray()
        return PhotoPayload(
            chat_id=chat_id,
            file_id=file_id,
            bytes=bytes(bytes_data),
            mime="image/jpeg",
        )
    except Exception:
        return None
