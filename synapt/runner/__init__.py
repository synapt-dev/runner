"""Generic runner kernel draft for Synapt research workloads."""

from .artifacts import (
    ArtifactSink,
    JsonlWriter,
    LocalArtifactSink,
    MarkdownSummary,
    write_jsonl,
)
from .gates import (
    GateCheck,
    GateExecution,
    GateFailed,
    GateResult,
    GeneratedCallCounter,
    run_pre_execution_gates,
    run_with_pre_execution_gates,
)
from .hashing import canonical_json, canonical_sha256, deterministic_seed
from .modal import (
    DEFAULT_GPU_COST_RATES,
    DashboardCostReconciliation,
    GpuCostRate,
    ModalBinding,
    ModalRuntimeSpec,
    build_modal_binding,
)
from .prereg import MethodGate, PreregistrationError, assert_method_allowed
from .records import (
    FailureRecord,
    RecordStatus,
    RunRecord,
    RunRecordError,
)
from .spans import (
    RenderMode,
    SpanOverlapError,
    SpanRenderResult,
    SpanUnit,
    render_span_units,
    reject_cross_selection_overlap,
)
from .wave import CellResult, CellSpec, WaveReport, run_wave

__all__ = [
    "ArtifactSink",
    "CellResult",
    "CellSpec",
    "DEFAULT_GPU_COST_RATES",
    "DashboardCostReconciliation",
    "FailureRecord",
    "GateCheck",
    "GateExecution",
    "GateFailed",
    "GateResult",
    "GeneratedCallCounter",
    "GpuCostRate",
    "JsonlWriter",
    "LocalArtifactSink",
    "MarkdownSummary",
    "MethodGate",
    "ModalBinding",
    "ModalRuntimeSpec",
    "PreregistrationError",
    "RecordStatus",
    "RenderMode",
    "RunRecord",
    "RunRecordError",
    "SpanOverlapError",
    "SpanRenderResult",
    "SpanUnit",
    "WaveReport",
    "assert_method_allowed",
    "build_modal_binding",
    "canonical_json",
    "canonical_sha256",
    "deterministic_seed",
    "reject_cross_selection_overlap",
    "render_span_units",
    "run_pre_execution_gates",
    "run_wave",
    "run_with_pre_execution_gates",
    "write_jsonl",
]
