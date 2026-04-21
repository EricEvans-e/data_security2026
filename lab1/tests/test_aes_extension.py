from pathlib import Path

from pir_lab.aes_mode import generate_aes_key, save_aes_key
from pir_lab.client import run_client_query
from pir_lab.server import PIRService, start_server


def test_aes_mode_query_recovers_plaintext(tmp_path: Path) -> None:
    key_file = tmp_path / "client_aes.key"
    save_aes_key(key_file, generate_aes_key())

    service = PIRService.from_args(mode="aes", count=4, dataset_file=None, key_file=str(key_file))
    handle = start_server(service, host="127.0.0.1", port=0)
    host, port = handle.address
    try:
        result = run_client_query(
            mode="aes",
            host=host,
            port=port,
            index=2,
            dataset_size=4,
            key_size=1024,
            key_file=str(key_file),
        )
    finally:
        handle.close()

    assert result.plaintext == service.messages[2]
