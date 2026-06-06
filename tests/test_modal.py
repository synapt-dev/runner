from __future__ import annotations

from synapt.runner.modal import (
    DashboardCostReconciliation,
    ModalRuntimeSpec,
    build_modal_binding,
    cost_rate_for_gpu,
)


class FakeSecret:
    @staticmethod
    def from_name(name: str) -> tuple[str, str]:
        return ("secret", name)


class FakeFunction:
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __call__(self, fn):
        return {"wrapped": fn.__name__, "kwargs": self.kwargs}


class FakeApp:
    def __init__(self, name: str):
        self.name = name
        self.function_kwargs = None

    def function(self, **kwargs):
        self.function_kwargs = kwargs
        return FakeFunction(kwargs)


class FakeModal:
    Secret = FakeSecret

    @staticmethod
    def App(name: str) -> FakeApp:
        return FakeApp(name)


def test_modal_binding_uses_fake_modal_without_importing_modal():
    def run_cell():
        return "ok"

    runtime = ModalRuntimeSpec(
        app_name="runner-test",
        gpu="A100-80GB",
        secrets=("hf",),
        max_containers=3,
    )

    binding = build_modal_binding(
        runtime=runtime,
        run_callable=run_cell,
        modal_module=FakeModal,
    )

    assert binding.app.name == "runner-test"
    assert binding.remote_function["wrapped"] == "run_cell"
    assert binding.remote_function["kwargs"]["gpu"] == "A100-80GB"
    assert binding.remote_function["kwargs"]["max_containers"] == 3
    assert binding.remote_function["kwargs"]["secrets"] == [("secret", "hf")]


def test_cost_rate_registry_and_dashboard_reconciliation():
    rate = cost_rate_for_gpu("A100-80GB", rates={"A100-80GB": 3.60})
    reconciliation = DashboardCostReconciliation(
        modeled_cost_usd=rate.cost_for_seconds(100),
        dashboard_completed_app_cost_usd=0.12,
        dashboard_total_cost_usd=0.13,
        failed_setup_cost_usd=0.01,
    )

    assert round(rate.cost_for_seconds(100), 2) == 0.10
    assert round(reconciliation.completed_delta_usd, 2) == 0.02
    assert round(reconciliation.total_delta_usd, 2) == 0.03
