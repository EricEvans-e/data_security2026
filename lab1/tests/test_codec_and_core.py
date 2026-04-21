from phe import paillier

from pir_lab.codec import decode_int_to_blob, decode_int_to_text, encode_blob_to_int, encode_text_to_int
from pir_lab.pir import aggregate_query, build_selection_vector, validate_index


def test_blob_and_text_roundtrip() -> None:
    raw = b"\x00abc\x10"
    assert decode_int_to_blob(encode_blob_to_int(raw)) == raw
    text = "record-01|name=Alice|score=95"
    assert decode_int_to_text(encode_text_to_int(text)) == text


def test_aggregate_query_recovers_selected_message() -> None:
    public_key, private_key = paillier.generate_paillier_keypair(n_length=512)
    messages = [encode_text_to_int(item) for item in ["m0", "m1", "m2"]]
    selection_vector = build_selection_vector(public_key, index=1, size=3)
    result = aggregate_query(public_key, messages, selection_vector)
    assert decode_int_to_text(private_key.decrypt(result)) == "m1"


def test_validate_index_rejects_invalid_position() -> None:
    try:
        validate_index(3, 3)
    except ValueError as exc:
        assert "index must be in" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("validate_index should raise ValueError")
