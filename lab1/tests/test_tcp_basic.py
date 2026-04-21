from pir_lab.client import run_client_query
from pir_lab.server import PIRService, start_server


def test_basic_tcp_query_recovers_selected_message() -> None:
    service = PIRService.from_args(mode="basic", count=5, dataset_file=None, key_file=None)
    handle = start_server(service, host="127.0.0.1", port=0)
    host, port = handle.address
    try:
        result = run_client_query(
            mode="basic",
            host=host,
            port=port,
            index=3,
            dataset_size=5,
            key_size=512,
        )
    finally:
        handle.close()

    assert result.plaintext == service.messages[3]
    assert result.request_bytes > result.response_bytes
