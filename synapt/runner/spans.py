"""Generic stable-unit span rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable, Mapping, Sequence


class RenderMode(StrEnum):
    DELETE = "delete"
    MASK = "mask"


class SpanOverlapError(ValueError):
    """Raised when selected spans cannot be rendered safely."""


@dataclass(frozen=True)
class SpanUnit:
    unit_id: int | str
    char_start: int
    char_end: int
    text: str
    protected: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.char_start < 0 or self.char_end < self.char_start:
            raise ValueError(
                f"invalid char span for {self.unit_id!r}: "
                f"{self.char_start}..{self.char_end}"
            )


@dataclass(frozen=True)
class SpanRenderResult:
    rendered_text: str
    rendered_unit_ids: tuple[int | str, ...]
    mode: RenderMode
    mask_token: str
    alignment_audit: Mapping[str, Any]


def render_span_units(
    *,
    text: str,
    units: Sequence[SpanUnit],
    selected_unit_ids: Iterable[int | str],
    mode: RenderMode | str,
    mask_token: str = "[MASKED]",
) -> SpanRenderResult:
    render_mode = RenderMode(mode)
    selected_ids = tuple(selected_unit_ids)
    selected_set = set(selected_ids)
    unit_by_id = {unit.unit_id: unit for unit in units}
    missing = [unit_id for unit_id in selected_ids if unit_id not in unit_by_id]
    if missing:
        raise SpanOverlapError(f"selected unit ids not present: {missing}")
    selected = tuple(unit_by_id[unit_id] for unit_id in selected_ids)
    protected = [unit.unit_id for unit in selected if unit.protected]
    if protected:
        raise SpanOverlapError(f"cannot render protected units: {protected}")
    _reject_overlapping_units(selected)

    rendered = text
    for unit in sorted(selected, key=lambda item: item.char_start, reverse=True):
        if rendered[unit.char_start : unit.char_end] != unit.text:
            raise SpanOverlapError(
                f"unit {unit.unit_id!r} text does not match source span"
            )
        replacement = "" if render_mode is RenderMode.DELETE else mask_token
        rendered = rendered[: unit.char_start] + replacement + rendered[unit.char_end :]

    return SpanRenderResult(
        rendered_text=rendered,
        rendered_unit_ids=selected_ids,
        mode=render_mode,
        mask_token=mask_token,
        alignment_audit={
            "selected_unit_ids": list(selected_ids),
            "selected_char_spans": [
                [unit.char_start, unit.char_end] for unit in selected
            ],
            "mode": render_mode.value,
            "source_length": len(text),
        },
    )


def reject_cross_selection_overlap(
    selections: Mapping[str, Iterable[int | str]],
) -> None:
    owner_by_unit: dict[int | str, str] = {}
    for arm_name, unit_ids in selections.items():
        for unit_id in unit_ids:
            if unit_id in owner_by_unit:
                raise SpanOverlapError(
                    "cross-selection overlap: "
                    f"{unit_id!r} appears in {owner_by_unit[unit_id]!r} and {arm_name!r}"
                )
            owner_by_unit[unit_id] = arm_name


def _reject_overlapping_units(units: Sequence[SpanUnit]) -> None:
    ordered = sorted(units, key=lambda item: (item.char_start, item.char_end))
    previous: SpanUnit | None = None
    for unit in ordered:
        if previous is not None and unit.char_start < previous.char_end:
            raise SpanOverlapError(
                f"overlapping selected units: {previous.unit_id!r}, {unit.unit_id!r}"
            )
        previous = unit
