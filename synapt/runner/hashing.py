"""Canonical JSON and deterministic hash helpers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def canonical_json(payload: Any) -> str:
    """Return stable, compact JSON for hashable runner artifacts."""

    return json.dumps(
        _jsonable(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def deterministic_seed(*parts: Any, bits: int = 64) -> int:
    if bits <= 0 or bits > 256:
        raise ValueError(f"bits must be in 1..256, got {bits}")
    digest = canonical_sha256(parts)
    hex_chars = (bits + 3) // 4
    value = int(digest[:hex_chars], 16)
    return value & ((1 << bits) - 1)


def _jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(val) for key, val in sorted(value.items())}
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    if isinstance(value, set | frozenset):
        return [_jsonable(item) for item in sorted(value, key=repr)]
    return value
