from __future__ import annotations

from synapt.runner.wave import CellSpec, run_wave


def test_wave_captures_per_cell_failures_without_aborting():
    cells = (
        CellSpec("ok", {"value": 1}),
        CellSpec("bad", {"value": 2}),
        CellSpec("ok-2", {"value": 3}),
    )

    def run_cell(cell: CellSpec):
        if cell.cell_id == "bad":
            raise RuntimeError("cell failed")
        return cell.payload["value"]

    report = run_wave(wave_id="wave-1", cells=cells, run_cell=run_cell)

    assert report.success_count == 2
    assert report.failure_count == 1
    assert [result.status for result in report.results] == [
        "SUCCESS",
        "FAILURE",
        "SUCCESS",
    ]
    assert report.results[1].failure_reason == "cell failed"
