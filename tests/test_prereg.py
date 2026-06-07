from __future__ import annotations

import pytest

from synapt.runner.prereg import (
    MethodGate,
    PreregistrationError,
    assert_method_allowed,
)


def test_prereg_gate_accepts_locked_method_and_version():
    gate = MethodGate.from_methods(
        preregistration_id="config#316",
        config_version="316",
        allowed_methods=("sentence_vorn",),
    )

    assert_method_allowed(
        method="sentence_vorn",
        gate=gate,
        runtime_preregistration_id="config#316",
        runtime_config_version="316",
    )


def test_prereg_gate_rejects_version_drift():
    gate = MethodGate.from_methods(
        preregistration_id="config#316",
        config_version="316",
        allowed_methods=("sentence_vorn",),
    )

    with pytest.raises(PreregistrationError, match="config version drift"):
        assert_method_allowed(
            method="sentence_vorn",
            gate=gate,
            runtime_preregistration_id="config#316",
            runtime_config_version="321",
        )


def test_prereg_gate_rejects_method_drift():
    gate = MethodGate.from_methods(
        preregistration_id="config#316",
        allowed_methods=("sentence_vorn",),
    )

    with pytest.raises(PreregistrationError, match="not allowed"):
        assert_method_allowed(
            method="sentence_snapkv",
            gate=gate,
            runtime_preregistration_id="config#316",
        )
