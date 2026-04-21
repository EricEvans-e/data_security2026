from __future__ import annotations

import json
from pathlib import Path

from .aes_mode import encrypt_message


def generate_demo_messages(count: int) -> list[str]:
    if count <= 0:
        raise ValueError("message count must be positive")
    names = [
        "Alice",
        "Bob",
        "Carol",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Heidi",
        "Ivan",
        "Judy",
        "Mallory",
        "Niaj",
        "Olivia",
        "Peggy",
        "Rupert",
        "Sybil",
    ]
    messages = []
    for index in range(count):
        name = names[index % len(names)]
        score = 82 + (index * 7) % 16
        dept = ["AI", "Security", "Networks", "Systems"][index % 4]
        messages.append(
            f"record-{index + 1:02d}|name={name}|dept={dept}|score={score}"
        )
    return messages


def load_messages(dataset_file: str | None, count: int) -> list[str]:
    if dataset_file is None:
        return generate_demo_messages(count)
    path = Path(dataset_file)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload or not all(
        isinstance(item, str) and item for item in payload
    ):
        raise ValueError("dataset file must be a non-empty JSON string list")
    return payload


def build_aes_ciphertext_store(messages: list[str], key: bytes) -> list[bytes]:
    if not messages:
        raise ValueError("messages must not be empty")
    return [encrypt_message(key, message) for message in messages]
