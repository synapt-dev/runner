from __future__ import annotations

import json

import pytest

from synapt.runner.hashing import canonical_json
from synapt.runner.modal import GenerationCostSurface
from synapt.runner.records import FailureRecord, RecordStatus, RunRecord, RunRecordError


def test_success_record_requires_prompt_and_quality_without_failure():
    record = RunRecord(
        run_id="run-1",
        record_status=RecordStatus.PROMPT_QUALITY_SUCCESS,
        prompt_record={"prompt_hash": "abc"},
        quality_record={"score": 1.0},
    )

    assert record.record_status is RecordStatus.PROMPT_QUALITY_SUCCESS


def test_success_record_carries_generation_cost_without_modal_cost():
    record = RunRecord(
        run_id="run-1",
        record_status=RecordStatus.PROMPT_QUALITY_SUCCESS,
        prompt_record={"prompt_hash": "abc"},
        quality_record={"score": 1.0},
        generation_cost=GenerationCostSurface(
            cost_usd=0.0025,
            source="provider_token_meter",
            model_id="Qwen/Qwen3-8B",
            prompt_tokens=1000,
            completion_tokens=25,
        ),
    )

    payload = json.loads(canonical_json(record))

    assert payload["generation_cost"]["surface"] == "generation_row"
    assert payload["generation_cost"]["cost_usd"] == 0.0025
    assert "dashboard_completed_app_cost_usd" not in payload["generation_cost"]


def test_success_record_rejects_missing_terminal_payloads():
    with pytest.raises(RunRecordError, match="requires prompt_record"):
        RunRecord(
            run_id="run-1",
            record_status=RecordStatus.PROMPT_QUALITY_SUCCESS,
        )


def test_runtime_failure_requires_failure_and_rejects_quality():
    with pytest.raises(RunRecordError, match="requires failure"):
        RunRecord(run_id="run-1", record_status=RecordStatus.RUNTIME_FAILURE)

    with pytest.raises(RunRecordError, match="cannot include quality_record"):
        RunRecord(
            run_id="run-1",
            record_status=RecordStatus.RUNTIME_FAILURE,
            failure=FailureRecord(reason="boom", stage="generate", message="x"),
            quality_record={"score": 0.0},
        )


def test_capacity_missing_requires_capacity_class():
    with pytest.raises(RunRecordError, match="requires capacity_missing_class"):
        RunRecord(
            run_id="run-1",
            record_status=RecordStatus.CAPACITY_MISSING,
            failure=FailureRecord(reason="oom", stage="load", message="CUDA OOM"),
        )

    record = RunRecord(
        run_id="run-1",
        record_status=RecordStatus.CAPACITY_MISSING,
        failure=FailureRecord(
            reason="oom",
            stage="load",
            message="CUDA OOM",
            capacity_missing_class="GPU_MEMORY",
        ),
    )

    assert record.failure is not None
    assert record.failure.capacity_missing_class == "GPU_MEMORY"


def test_unknown_record_status_uses_runner_error_type():
    with pytest.raises(RunRecordError, match="unknown record_status"):
        RunRecord(run_id="run-1", record_status="AMBIGUOUS")  # type: ignore[arg-type]
