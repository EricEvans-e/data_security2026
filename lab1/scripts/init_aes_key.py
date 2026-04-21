from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pir_lab.client import init_aes_key_file


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/init_aes_key.py <output-key-file>")
    init_aes_key_file(sys.argv[1])


if __name__ == "__main__":
    main()
