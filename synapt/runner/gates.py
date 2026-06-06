"""Pre-execution gates that fail closed before model calls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


class GateFailed(RuntimeError):
    """Raised when a pre-execution gate rejects the run."""


@dataclass(frozen=True)
class GateCheck:
    name: str
    check: Callable[[], None]


@dataclass(frozen=True)
class GateResult:
    ok: bool
    failed_gate: str | None
    reason: str | None
    generated_calls: int


@dataclass(frozen=True)
class GateExecution:
    gate_result: GateResult
    output: Any | None = None


class GeneratedCallCounter:
    """Tiny test helper for proving gates reject before generation."""

    def __init__(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def record(self) -> None:
        self._count += 1


def run_pre_execution_gates(
    gates: Iterable[GateCheck],
    *,
    generated_call_counter: GeneratedCallCounter | None = None,
) -> GateResult:
    counter = generated_call_counter or GeneratedCallCounter()
    for gate in gates:
        try:
            gate.check()
        except Exception as exc:
            return GateResult(
                ok=False,
                failed_gate=gate.name,
                reason=str(exc),
                generated_calls=counter.count,
            )
    return GateResult(
        ok=True,
        failed_gate=None,
        reason=None,
        generated_calls=counter.count,
    )


def run_with_pre_execution_gates(
    gates: Iterable[GateCheck],
    operation: Callable[[], Any],
    *,
    generated_call_counter: GeneratedCallCounter | None = None,
) -> GateExecution:
    counter = generated_call_counter or GeneratedCallCounter()
    result = run_pre_execution_gates(gates, generated_call_counter=counter)
    if not result.ok:
        return GateExecution(gate_result=result, output=None)
    return GateExecution(gate_result=result, output=operation())
