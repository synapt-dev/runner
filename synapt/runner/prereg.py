"""Preregistration method and version gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class PreregistrationError(ValueError):
    """Raised when runtime configuration drifts from a locked preregistration."""


@dataclass(frozen=True)
class MethodGate:
    preregistration_id: str
    allowed_methods: frozenset[str]
    config_version: str | None = None

    @classmethod
    def from_methods(
        cls,
        *,
        preregistration_id: str,
        allowed_methods: Iterable[str],
        config_version: str | None = None,
    ) -> "MethodGate":
        return cls(
            preregistration_id=preregistration_id,
            allowed_methods=frozenset(allowed_methods),
            config_version=config_version,
        )


def assert_method_allowed(
    *,
    method: str,
    gate: MethodGate,
    runtime_preregistration_id: str,
    runtime_config_version: str | None = None,
) -> None:
    if runtime_preregistration_id != gate.preregistration_id:
        raise PreregistrationError(
            "preregistration id drift: "
            f"expected {gate.preregistration_id!r}, got {runtime_preregistration_id!r}"
        )
    if gate.config_version is not None and runtime_config_version != gate.config_version:
        raise PreregistrationError(
            "config version drift: "
            f"expected {gate.config_version!r}, got {runtime_config_version!r}"
        )
    if method not in gate.allowed_methods:
        allowed = ", ".join(sorted(gate.allowed_methods))
        raise PreregistrationError(
            f"method {method!r} is not allowed by preregistration; allowed={allowed}"
        )
