from __future__ import annotations

import pytest

from synapt.runner.spans import (
    RenderMode,
    SpanOverlapError,
    SpanUnit,
    reject_cross_selection_overlap,
    render_span_units,
)


TEXT = "alpha beta gamma"
UNITS = (
    SpanUnit(unit_id=1, char_start=0, char_end=5, text="alpha"),
    SpanUnit(unit_id=2, char_start=6, char_end=10, text="beta"),
    SpanUnit(unit_id=3, char_start=11, char_end=16, text="gamma", protected=True),
)


def test_span_delete_rendering_uses_descending_spans():
    result = render_span_units(
        text=TEXT,
        units=UNITS,
        selected_unit_ids=(1, 2),
        mode=RenderMode.DELETE,
    )

    assert result.rendered_text == "  gamma"
    assert result.alignment_audit["selected_unit_ids"] == [1, 2]


def test_span_mask_rendering_preserves_marker():
    result = render_span_units(
        text=TEXT,
        units=UNITS,
        selected_unit_ids=(2,),
        mode=RenderMode.MASK,
        mask_token="[MASKED_SEMU]",
    )

    assert result.rendered_text == "alpha [MASKED_SEMU] gamma"
    assert result.mask_token == "[MASKED_SEMU]"


def test_span_rendering_rejects_protected_units():
    with pytest.raises(SpanOverlapError, match="protected"):
        render_span_units(
            text=TEXT,
            units=UNITS,
            selected_unit_ids=(3,),
            mode=RenderMode.DELETE,
        )


def test_span_rendering_rejects_overlapping_units():
    with pytest.raises(SpanOverlapError, match="overlapping"):
        render_span_units(
            text=TEXT,
            units=(
                SpanUnit(unit_id="a", char_start=0, char_end=7, text="alpha b"),
                SpanUnit(unit_id="b", char_start=5, char_end=10, text=" beta"),
            ),
            selected_unit_ids=("a", "b"),
            mode=RenderMode.DELETE,
        )


def test_cross_selection_overlap_fails_closed():
    with pytest.raises(SpanOverlapError, match="cross-selection overlap"):
        reject_cross_selection_overlap(
            {
                "vorn_high": (1, 2),
                "snapkv_high": (3, 2),
            }
        )
