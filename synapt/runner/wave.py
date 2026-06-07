"""Wave fanout helpers with per-cell failure capture."""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Callable, Iterable, Mapping


@dataclass(frozen=True)
class CellSpec:
    cell_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CellResult:
    cell_id: str
    status: str
    output: Any | None = None
    failure_reason: str | None = None
    runtime_seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status == "SUCCESS"


@dataclass(frozen=True)
class WaveReport:
    wave_id: str
    results: tuple[CellResult, ...]

    @property
    def success_count(self) -> int:
        return sum(1 for result in self.results if result.ok)

    @property
    def failure_count(self) -> int:
        return len(self.results) - self.success_count


def run_wave(
    *,
    wave_id: str,
    cells: Iterable[CellSpec],
    run_cell: Callable[[CellSpec], Any],
) -> WaveReport:
    results: list[CellResult] = []
    for cell in cells:
        start = time.perf_counter()
        try:
            output = run_cell(cell)
        except Exception as exc:
            results.append(
                CellResult(
                    cell_id=cell.cell_id,
                    status="FAILURE",
                    failure_reason=str(exc),
                    runtime_seconds=time.perf_counter() - start,
                )
            )
            continue
        results.append(
            CellResult(
                cell_id=cell.cell_id,
                status="SUCCESS",
                output=output,
                runtime_seconds=time.perf_counter() - start,
            )
        )
    return WaveReport(wave_id=wave_id, results=tuple(results))
