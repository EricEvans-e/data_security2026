from __future__ import annotations

import json
import statistics
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pir_lab.aes_mode import generate_aes_key, save_aes_key
from pir_lab.client import run_client_query
from pir_lab.server import PIRService, start_server


RUNS_PER_CASE = 3


def run_case(mode: str, count: int, key_size: int) -> dict[str, float | int | str]:
    with TemporaryDirectory() as temp_dir:
        key_file = None
        if mode == "aes":
            key_path = Path(temp_dir) / "benchmark_aes.key"
            save_aes_key(key_path, generate_aes_key())
            key_file = str(key_path)

        service = PIRService.from_args(
            mode=mode,
            count=count,
            dataset_file=None,
            key_file=key_file,
        )
        handle = start_server(service, host="127.0.0.1", port=0)
        host, port = handle.address
        results = []
        try:
            for run_id in range(RUNS_PER_CASE):
                index = (run_id * 5 + 1) % count
                result = run_client_query(
                    mode=mode,
                    host=host,
                    port=port,
                    index=index,
                    dataset_size=count,
                    key_size=key_size,
                    key_file=key_file,
                )
                results.append(result)
        finally:
            handle.close()

    total_times = [
        item.keygen_ms + item.query_build_ms + item.network_ms + item.decrypt_ms
        for item in results
    ]
    return {
        "mode": mode,
        "count": count,
        "key_size": key_size,
        "avg_total_ms": round(statistics.mean(total_times), 2),
        "avg_keygen_ms": round(statistics.mean(item.keygen_ms for item in results), 2),
        "avg_query_build_ms": round(
            statistics.mean(item.query_build_ms for item in results), 2
        ),
        "avg_network_ms": round(statistics.mean(item.network_ms for item in results), 2),
        "avg_decrypt_ms": round(statistics.mean(item.decrypt_ms for item in results), 2),
        "avg_request_bytes": round(
            statistics.mean(item.request_bytes for item in results), 2
        ),
        "avg_response_bytes": round(
            statistics.mean(item.response_bytes for item in results), 2
        ),
    }


def format_table(rows: list[dict[str, float | int | str]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    lines = [header, divider]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    dataset_rows = [run_case("basic", count, 2048) for count in (8, 16, 32, 64)]
    key_rows = [run_case("basic", 16, key_size) for key_size in (1024, 2048, 3072)]
    mode_rows = [run_case(mode, 16, 2048) for mode in ("basic", "aes")]

    output = {
        "dataset_scale": dataset_rows,
        "key_size_scale": key_rows,
        "mode_compare": mode_rows,
    }

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    json_path = results_dir / "benchmark_results.json"
    markdown_path = results_dir / "benchmark_tables.md"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    sections = [
        "# Benchmark Tables",
        "## Dataset Scale",
        format_table(
            dataset_rows,
            [
                "count",
                "key_size",
                "avg_total_ms",
                "avg_request_bytes",
                "avg_response_bytes",
            ],
        ),
        "",
        "## Key Size Scale",
        format_table(
            key_rows,
            [
                "count",
                "key_size",
                "avg_total_ms",
                "avg_request_bytes",
                "avg_response_bytes",
            ],
        ),
        "",
        "## Mode Compare",
        format_table(
            mode_rows,
            [
                "mode",
                "count",
                "key_size",
                "avg_total_ms",
                "avg_request_bytes",
                "avg_response_bytes",
            ],
        ),
    ]
    markdown_path.write_text("\n".join(sections) + "\n", encoding="utf-8")

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
