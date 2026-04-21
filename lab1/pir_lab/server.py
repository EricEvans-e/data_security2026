from __future__ import annotations

import argparse
import json
import logging
import socketserver
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .aes_mode import load_aes_key
from .codec import encode_blob_to_int, encode_text_to_int
from .dataset import build_aes_ciphertext_store, load_messages
from .pir import aggregate_query
from .protocol import (
    deserialize_encrypted_number,
    deserialize_public_key,
    recv_message,
    send_message,
    serialize_encrypted_number,
)


LOGGER = logging.getLogger(__name__)


@dataclass
class PIRService:
    mode: str
    messages: list[str]
    aes_packages: list[bytes] | None = None

    @property
    def dataset_size(self) -> int:
        return len(self.messages)

    @classmethod
    def from_args(
        cls,
        mode: str,
        count: int,
        dataset_file: str | None,
        key_file: str | None,
    ) -> "PIRService":
        messages = load_messages(dataset_file=dataset_file, count=count)
        if mode == "basic":
            return cls(mode=mode, messages=messages)
        if not key_file:
            raise ValueError("AES mode requires --key-file")
        key = load_aes_key(key_file)
        packages = build_aes_ciphertext_store(messages, key)
        return cls(mode=mode, messages=messages, aes_packages=packages)

    def build_plaintexts(self) -> list[int]:
        if self.mode == "basic":
            return [encode_text_to_int(message) for message in self.messages]
        if not self.aes_packages:
            raise ValueError("AES ciphertext store is not initialized")
        return [encode_blob_to_int(package) for package in self.aes_packages]

    def handle_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("protocol") != "pir-lab1":
            raise ValueError("unsupported protocol")
        if payload.get("mode") != self.mode:
            raise ValueError(f"server mode is {self.mode}, but request mode is {payload.get('mode')}")
        public_key = deserialize_public_key(payload["public_key"])
        selection_vector = [
            deserialize_encrypted_number(public_key, item)
            for item in payload["selection_vector"]
        ]
        plaintexts = self.build_plaintexts()
        result = aggregate_query(public_key, plaintexts, selection_vector)
        return {
            "protocol": "pir-lab1",
            "mode": self.mode,
            "dataset_size": self.dataset_size,
            "result": serialize_encrypted_number(result),
            "message_encoding": "utf-8-int" if self.mode == "basic" else "aes-gcm-package-int",
        }


class _ThreadedTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _RequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        service: PIRService = self.server.service  # type: ignore[attr-defined]
        try:
            payload, request_bytes = recv_message(self.request)
            LOGGER.info(
                "received query: mode=%s, dataset_size=%s, request_bytes=%s",
                payload.get("mode"),
                service.dataset_size,
                request_bytes,
            )
            response = service.handle_query(payload)
        except Exception as exc:  # pragma: no cover - exercised in integration flow
            LOGGER.exception("failed to process client request")
            response = {"protocol": "pir-lab1", "status": "error", "message": str(exc)}
        send_message(self.request, response)


@dataclass
class ServerHandle:
    server: _ThreadedTCPServer
    thread: threading.Thread

    @property
    def address(self) -> tuple[str, int]:
        host, port = self.server.server_address
        return str(host), int(port)

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def start_server(
    service: PIRService,
    host: str = "127.0.0.1",
    port: int = 0,
) -> ServerHandle:
    server = _ThreadedTCPServer((host, port), _RequestHandler)
    server.service = service  # type: ignore[attr-defined]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return ServerHandle(server=server, thread=thread)


def run_server(
    mode: str,
    host: str,
    port: int,
    count: int,
    dataset_file: str | None,
    key_file: str | None,
) -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    service = PIRService.from_args(mode=mode, count=count, dataset_file=dataset_file, key_file=key_file)
    preview = service.messages[: min(3, len(service.messages))]
    LOGGER.info("server mode=%s host=%s port=%s dataset_size=%s", mode, host, port, service.dataset_size)
    LOGGER.info("dataset preview=%s", json.dumps(preview, ensure_ascii=False))
    handle = start_server(service=service, host=host, port=port)
    actual_host, actual_port = handle.address
    print(f"SERVER_READY mode={mode} host={actual_host} port={actual_port} dataset_size={service.dataset_size}")
    try:
        handle.thread.join()
    except KeyboardInterrupt:
        print("\nserver shutting down")
        handle.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Paillier PIR lab TCP server")
    parser.add_argument("--mode", choices=["basic", "aes"], required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9101)
    parser.add_argument("--count", type=int, default=16)
    parser.add_argument("--dataset-file")
    parser.add_argument("--key-file")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_server(
        mode=args.mode,
        host=args.host,
        port=args.port,
        count=args.count,
        dataset_file=args.dataset_file,
        key_file=args.key_file,
    )


if __name__ == "__main__":
    main()
