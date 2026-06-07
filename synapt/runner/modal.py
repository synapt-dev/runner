"""Modal runtime metadata and cost accounting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


DEFAULT_GPU_COST_RATES: Mapping[str, float] = {
    "A100-80GB": 4.00,
    "H100": 7.50,
    "H200": 10.00,
}


@dataclass(frozen=True)
class ModalRuntimeSpec:
    app_name: str
    gpu: str = "A100-80GB"
    timeout_seconds: int = 60 * 60
    modal_profile: str = "layne1penney"
    max_containers: int = 1
    volume_name: str | None = None
    volume_path: str | None = None
    secrets: tuple[str, ...] = ()
    env_vars: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class GpuCostRate:
    gpu: str
    dollars_per_hour: float

    def cost_for_seconds(self, seconds: float) -> float:
        if seconds < 0:
            raise ValueError("seconds cannot be negative")
        return self.dollars_per_hour * (seconds / 3600.0)


@dataclass(frozen=True)
class GenerationCostSurface:
    """Per-row model generation cost, not Modal wall-clock billing."""

    cost_usd: float
    source: str
    model_id: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    notes: tuple[str, ...] = ()
    surface: str = "generation_row"

    def __post_init__(self) -> None:
        if self.cost_usd < 0:
            raise ValueError("cost_usd cannot be negative")
        for field_name in ("prompt_tokens", "completion_tokens", "cached_tokens"):
            value = getattr(self, field_name)
            if value is not None and value < 0:
                raise ValueError(f"{field_name} cannot be negative")

    @property
    def total_tokens(self) -> int | None:
        token_counts = (self.prompt_tokens, self.completion_tokens)
        if any(value is None for value in token_counts):
            return None
        return sum(value for value in token_counts if value is not None)


@dataclass(frozen=True)
class DashboardCostReconciliation:
    modeled_cost_usd: float
    dashboard_completed_app_cost_usd: float | None = None
    dashboard_total_cost_usd: float | None = None
    failed_setup_cost_usd: float | None = None
    notes: tuple[str, ...] = ()

    @property
    def completed_delta_usd(self) -> float | None:
        if self.dashboard_completed_app_cost_usd is None:
            return None
        return self.dashboard_completed_app_cost_usd - self.modeled_cost_usd

    @property
    def total_delta_usd(self) -> float | None:
        if self.dashboard_total_cost_usd is None:
            return None
        return self.dashboard_total_cost_usd - self.modeled_cost_usd


@dataclass(frozen=True)
class ModalWallClockCostSurface:
    """Modal app/runtime cost, separate from per-row generation cost."""

    runtime_seconds: float
    gpu: str
    reconciliation: DashboardCostReconciliation | None = None
    modal_app_id: str | None = None
    modal_call_id: str | None = None
    notes: tuple[str, ...] = ()
    surface: str = "modal_wall_clock"

    def __post_init__(self) -> None:
        if self.runtime_seconds < 0:
            raise ValueError("runtime_seconds cannot be negative")


@dataclass(frozen=True)
class ModalBinding:
    runtime: ModalRuntimeSpec
    app: Any
    remote_function: Any
    entrypoint_name: str


def cost_rate_for_gpu(
    gpu: str,
    *,
    rates: Mapping[str, float] = DEFAULT_GPU_COST_RATES,
) -> GpuCostRate:
    try:
        return GpuCostRate(gpu=gpu, dollars_per_hour=rates[gpu])
    except KeyError as exc:
        raise ValueError(f"no cost rate registered for GPU {gpu!r}") from exc


def build_modal_binding(
    *,
    runtime: ModalRuntimeSpec,
    run_callable: Callable[..., Any],
    modal_module: Any,
    image: Any = None,
    volumes: Mapping[str, Any] | None = None,
    entrypoint_name: str | None = None,
) -> ModalBinding:
    """Bind a callable to Modal without importing Modal at module import time."""

    app = modal_module.App(runtime.app_name)
    function_kwargs: dict[str, Any] = {
        "gpu": runtime.gpu,
        "timeout": runtime.timeout_seconds,
        "max_containers": runtime.max_containers,
    }
    if image is not None:
        function_kwargs["image"] = image
    if volumes:
        function_kwargs["volumes"] = dict(volumes)
    if runtime.secrets:
        function_kwargs["secrets"] = [
            modal_module.Secret.from_name(name) for name in runtime.secrets
        ]
    decorator = app.function(**function_kwargs)
    remote_function = decorator(run_callable)
    return ModalBinding(
        runtime=runtime,
        app=app,
        remote_function=remote_function,
        entrypoint_name=entrypoint_name or run_callable.__name__,
    )
