from __future__ import annotations

from typing import Final


_SENTINEL: Final[bytes] = b"\x01"


def encode_blob_to_int(data: bytes) -> int:
    if not data:
        raise ValueError("data must not be empty")
    return int.from_bytes(_SENTINEL + data, "big")


def decode_int_to_blob(value: int) -> bytes:
    if value <= 0:
        raise ValueError("value must be positive")
    size = max(1, (value.bit_length() + 7) // 8)
    raw = value.to_bytes(size, "big")
    if not raw.startswith(_SENTINEL):
        raise ValueError("decoded payload is missing sentinel prefix")
    payload = raw[len(_SENTINEL) :]
    if not payload:
        raise ValueError("decoded payload must not be empty")
    return payload


def encode_text_to_int(text: str) -> int:
    if not text:
        raise ValueError("text must not be empty")
    return encode_blob_to_int(text.encode("utf-8"))


def decode_int_to_text(value: int) -> str:
    return decode_int_to_blob(value).decode("utf-8")
