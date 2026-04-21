from __future__ import annotations

import base64
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32


def generate_aes_key() -> bytes:
    return get_random_bytes(KEY_SIZE)


def save_aes_key(path: str | Path, key: bytes) -> None:
    Path(path).write_text(base64.b64encode(key).decode("ascii"), encoding="utf-8")


def load_aes_key(path: str | Path) -> bytes:
    key = base64.b64decode(Path(path).read_text(encoding="utf-8").strip())
    if len(key) != KEY_SIZE:
        raise ValueError(f"AES key must be {KEY_SIZE} bytes, got {len(key)}")
    return key


def encrypt_message(key: bytes, plaintext: str) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_SIZE))
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
    return cipher.nonce + tag + ciphertext


def decrypt_message(key: bytes, package: bytes) -> str:
    if len(package) <= NONCE_SIZE + TAG_SIZE:
        raise ValueError("AES package is too short")
    nonce = package[:NONCE_SIZE]
    tag = package[NONCE_SIZE : NONCE_SIZE + TAG_SIZE]
    ciphertext = package[NONCE_SIZE + TAG_SIZE :]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode("utf-8")
