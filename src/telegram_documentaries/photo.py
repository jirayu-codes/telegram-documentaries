from __future__ import annotations

import logging
from typing import Any

from . import logging as tlog
from .types import PhotoPayload

LOGGER = logging.getLogger("telegram_documentaries")


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
        LOGGER.exception("event=photo.download.error file_id=%s", file_id)
        return None
