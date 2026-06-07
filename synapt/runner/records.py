"""Terminal run-record invariants."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .modal import GenerationCostSurface


class RecordStatus(StrEnum):
    PROMPT_QUALITY_SUCCESS = "PROMPT_QUALITY_SUCCESS"
    RUNTIME_FAILURE = "RUNTIME_FAILURE"
    CAPACITY_MISSING = "CAPACITY_MISSING"


class RunRecordError(ValueError):
    """Raised when a run record would make terminal status ambiguous."""


@dataclass(frozen=True)
class FailureRecord:
    reason: str
    stage: str
    message: str
    capacity_missing_class: str | None = None
    retry_count: int = 0
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    record_status: RecordStatus
    prompt_record: Mapping[str, Any] | None = None
    quality_record: Mapping[str, Any] | None = None
    generation_cost: GenerationCostSurface | None = None
    failure: FailureRecord | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        try:
            status = RecordStatus(self.record_status)
        except ValueError as exc:
            raise RunRecordError(
                f"unknown record_status: {self.record_status}"
            ) from exc
        object.__setattr__(self, "record_status", status)
        if status is RecordStatus.PROMPT_QUALITY_SUCCESS:
            self._require_success_path()
            return
        if status is RecordStatus.RUNTIME_FAILURE:
            self._require_failure_path(capacity_required=False)
            return
        if status is RecordStatus.CAPACITY_MISSING:
            self._require_failure_path(capacity_required=True)
            return

    def _require_success_path(self) -> None:
        if self.prompt_record is None or self.quality_record is None:
            raise RunRecordError(
                "PROMPT_QUALITY_SUCCESS requires prompt_record and quality_record"
            )
        if self.failure is not None:
            raise RunRecordError("PROMPT_QUALITY_SUCCESS cannot include failure")

    def _require_failure_path(self, *, capacity_required: bool) -> None:
        if self.failure is None:
            raise RunRecordError(f"{self.record_status} requires failure")
        if self.quality_record is not None:
            raise RunRecordError(f"{self.record_status} cannot include quality_record")
        if capacity_required and not self.failure.capacity_missing_class:
            raise RunRecordError("CAPACITY_MISSING requires capacity_missing_class")
