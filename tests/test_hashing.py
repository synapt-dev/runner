from __future__ import annotations

from dataclasses import dataclass

from synapt.runner.hashing import canonical_json, canonical_sha256, deterministic_seed


@dataclass(frozen=True)
class Payload:
    b: int
    a: tuple[int, ...]


def test_canonical_json_sorts_keys_and_compacts():
    assert canonical_json({"b": 2, "a": [1]}) == '{"a":[1],"b":2}'


def test_canonical_hash_is_stable_for_dataclasses():
    payload = Payload(b=2, a=(1, 3))

    assert canonical_sha256(payload) == canonical_sha256({"a": [1, 3], "b": 2})


def test_deterministic_seed_is_stable_and_bounded():
    seed = deterministic_seed("run", {"case": 1}, bits=32)

    assert seed == deterministic_seed("run", {"case": 1}, bits=32)
    assert 0 <= seed < 2**32
