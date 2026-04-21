from pathlib import Path


def build_witness(x: int) -> dict[str, int]:
    x_square = x * x
    x_cube = x_square * x
    sum_with_x = x_cube + x
    expr_out = sum_with_x + 5
    return {
        "x": x,
        "x_square": x_square,
        "x_cube": x_cube,
        "sum_with_x": sum_with_x,
        "expr_out": expr_out,
    }


def test_valid_default_witness():
    witness = build_witness(3)
    assert witness["expr_out"] == 35


def test_invalid_witness_for_public_output():
    witness = build_witness(4)
    assert witness["expr_out"] != 35


def test_lab2_directories_exist():
    root = Path(__file__).resolve().parents[1]
    for name in ["zk_lab", "scripts", "results", "report", "src"]:
        assert (root / name).exists(), f"missing {name}"
