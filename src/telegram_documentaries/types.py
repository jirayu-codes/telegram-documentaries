from __future__ import annotations

from pydantic import BaseModel


class PhotoPayload(BaseModel):
    chat_id: int | str
    file_id: str
    bytes: bytes
    mime: str = "image/jpeg"


class ClassificationResult(BaseModel):
    is_human: bool
    reason: str
