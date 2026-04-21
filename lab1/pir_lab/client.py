from __future__ import annotations

import argparse
import json
import random
import socket
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from phe import paillier

from .aes_mode import generate_aes_key, load_aes_key, save_aes_key, decrypt_message
from .codec import decode_int_to_blob, decode_int_to_text
from .pir import build_selection_vector, validate_index
from .protocol import (
    recv_message,
    send_message,
    serialize_encrypted_number,
    serialize_public_key,
)


@dataclass
class QueryResult:
    mode: str
    index: int
    dataset_size: int
    key_size: int
    request_bytes: int
    response_bytes: int
    keygen_ms: float
    query_build_ms: float
    network_ms: float
    decrypt_ms: float
    plaintext: str


def init_aes_key_file(key_file: str) -> None:
    path = Path(key_file)
    key = generate_aes_key()
    save_aes_key(path, key)
    print(f"AES key written to {path}")


def run_client_query(
    mode: str,
    host: str,
    port: int,
    index: int,
    dataset_size: int,
    key_size: int,
    key_file: str | None = None,
) -> QueryResult:
    validate_index(index, dataset_size)

    keygen_start = perf_counter()
    public_key, private_key = paillier.generate_paillier_keypair(n_length=key_size)
    keygen_ms = (perf_counter() - keygen_start) * 1000

    build_start = perf_counter()
    selection_vector = build_selection_vector(public_key, index, dataset_size)
    request = {
        "protocol": "pir-lab1",
        "mode": mode,
        "public_key": serialize_public_key(public_key),
        "selection_vector": [serialize_encrypted_number(item) for item in selection_vector],
    }
    query_build_ms = (perf_counter() - build_start) * 1000

    network_start = perf_counter()
    with socket.create_connection((host, port), timeout=30) as sock:
        request_bytes = send_message(sock, request)
        response, response_bytes = recv_message(sock)
    network_ms = (perf_counter() - network_start) * 1000

    if response.get("status") == "error":
        raise RuntimeError(response["message"])

    decrypt_start = perf_counter()
    result = paillier.EncryptedNumber(
        public_key, int(response["result"]["ciphertext"]), int(response["result"]["exponent"])
    )
    recovered_value = private_key.decrypt(result)
    if mode == "basic":
        plaintext = decode_int_to_text(recovered_value)
    else:
        if not key_file:
            raise ValueError("AES mode requires --key-file")
        plaintext = decrypt_message(load_aes_key(key_file), decode_int_to_blob(recovered_value))
    decrypt_ms = (perf_counter() - decrypt_start) * 1000

    return QueryResult(
        mode=mode,
        index=index,
        dataset_size=dataset_size,
        key_size=key_size,
        request_bytes=request_bytes,
        response_bytes=response_bytes,
        keygen_ms=keygen_ms,
        query_build_ms=query_build_ms,
        network_ms=network_ms,
        decrypt_ms=decrypt_ms,
        plaintext=plaintext,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Paillier PIR lab TCP client")
    parser.add_argument("--mode", choices=["basic", "aes"])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9101)
    parser.add_argument("--index", type=int)
    parser.add_argument("--dataset-size", type=int, default=16)
    parser.add_argument("--key-size", type=int, default=2048)
    parser.add_argument("--key-file")
    parser.add_argument("--random-index", action="store_true")
    parser.add_argument("--init-key-file")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.init_key_file:
        init_aes_key_file(args.init_key_file)
        return

    if args.index is None and not args.random_index:
        raise SystemExit("provide --index or --random-index")
    index = args.index if args.index is not None else random.randrange(args.dataset_size)
    result = run_client_query(
        mode=args.mode,
        host=args.host,
        port=args.port,
        index=index,
        dataset_size=args.dataset_size,
        key_size=args.key_size,
        key_file=args.key_file,
    )
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
