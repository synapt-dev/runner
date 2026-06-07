from __future__ import annotations

from synapt.runner.gates import (
    GateCheck,
    GeneratedCallCounter,
    run_pre_execution_gates,
    run_with_pre_execution_gates,
)


def test_pre_execution_gate_rejects_before_generation_call():
    counter = GeneratedCallCounter()

    def fail() -> None:
        raise ValueError("mask token count drift")

    def generate() -> str:
        counter.record()
        return "generated"

    execution = run_with_pre_execution_gates(
        [GateCheck("mask-dry-run", fail)],
        generate,
        generated_call_counter=counter,
    )

    assert execution.output is None
    assert execution.gate_result.ok is False
    assert execution.gate_result.failed_gate == "mask-dry-run"
    assert execution.gate_result.generated_calls == 0
    assert counter.count == 0


def test_pre_execution_gate_calls_operation_after_all_gates_pass():
    counter = GeneratedCallCounter()

    def generate() -> str:
        counter.record()
        return "generated"

    execution = run_with_pre_execution_gates(
        [GateCheck("ok", lambda: None)],
        generate,
        generated_call_counter=counter,
    )

    assert execution.gate_result.ok is True
    assert execution.output == "generated"
    assert counter.count == 1


def test_run_pre_execution_gates_reports_current_generated_count():
    counter = GeneratedCallCounter()
    counter.record()

    result = run_pre_execution_gates(
        [GateCheck("ok", lambda: None)],
        generated_call_counter=counter,
    )

    assert result.ok is True
    assert result.generated_calls == 1
