from __future__ import annotations

import json
import socket
import struct
from typing import Any

from phe import paillier


def serialize_public_key(public_key: paillier.PaillierPublicKey) -> dict[str, str]:
    return {"n": str(public_key.n)}


def deserialize_public_key(payload: dict[str, Any]) -> paillier.PaillierPublicKey:
    return paillier.PaillierPublicKey(n=int(payload["n"]))


def serialize_encrypted_number(value: paillier.EncryptedNumber) -> dict[str, str | int]:
    return {
        "ciphertext": str(value.ciphertext(False)),
        "exponent": value.exponent,
    }


def deserialize_encrypted_number(
    public_key: paillier.PaillierPublicKey, payload: dict[str, Any]
) -> paillier.EncryptedNumber:
    return paillier.EncryptedNumber(
        public_key=public_key,
        ciphertext=int(payload["ciphertext"]),
        exponent=int(payload.get("exponent", 0)),
    )


def dumps_message(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def send_message(sock: socket.socket, payload: dict[str, Any]) -> int:
    body = dumps_message(payload)
    sock.sendall(struct.pack("!I", len(body)))
    sock.sendall(body)
    return len(body) + 4


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("socket closed before message was fully received")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_message(sock: socket.socket) -> tuple[dict[str, Any], int]:
    header = recv_exact(sock, 4)
    size = struct.unpack("!I", header)[0]
    body = recv_exact(sock, size)
    return json.loads(body.decode("utf-8")), size + 4
