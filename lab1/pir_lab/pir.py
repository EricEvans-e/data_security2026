from __future__ import annotations

from phe import paillier


def validate_index(index: int, size: int) -> None:
    if size <= 0:
        raise ValueError("dataset size must be positive")
    if not 0 <= index < size:
        raise ValueError(f"index must be in [0, {size - 1}], got {index}")


def build_selection_vector(
    public_key: paillier.PaillierPublicKey, index: int, size: int
) -> list[paillier.EncryptedNumber]:
    validate_index(index, size)
    return [public_key.encrypt(int(position == index)) for position in range(size)]


def validate_plaintexts(plaintexts: list[int], public_key: paillier.PaillierPublicKey) -> None:
    if not plaintexts:
        raise ValueError("plaintext dataset must not be empty")
    limit = public_key.max_int
    for value in plaintexts:
        if value <= 0:
            raise ValueError("plaintext values must be positive integers")
        if value > limit:
            raise ValueError(
                "plaintext integer exceeds Paillier max_int; "
                "reduce message size or use a larger key length"
            )


def aggregate_query(
    public_key: paillier.PaillierPublicKey,
    plaintexts: list[int],
    selection_vector: list[paillier.EncryptedNumber],
) -> paillier.EncryptedNumber:
    if len(plaintexts) != len(selection_vector):
        raise ValueError("plaintext dataset and selection vector must have identical length")
    validate_plaintexts(plaintexts, public_key)
    result = public_key.encrypt(0)
    for plaintext, encrypted_selector in zip(plaintexts, selection_vector, strict=True):
        result += encrypted_selector * plaintext
    return result
