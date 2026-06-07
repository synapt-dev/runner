from __future__ import annotations

import json

from synapt.runner.artifacts import LocalArtifactSink, MarkdownSummary, write_jsonl


def test_jsonl_writer_uses_canonical_json(tmp_path):
    path = tmp_path / "records.jsonl"

    write_jsonl(path, [{"b": 2, "a": 1}, {"z": [3, 2, 1]}])

    assert path.read_text().splitlines() == [
        '{"a":1,"b":2}',
        '{"z":[3,2,1]}',
    ]


def test_local_sink_writes_json_jsonl_and_markdown(tmp_path):
    sink = LocalArtifactSink(tmp_path)

    json_path = sink.write_json("payload.json", {"b": 2, "a": 1})
    jsonl_path = sink.write_jsonl("rows.jsonl", [{"row": 1}])
    md_path = sink.write_markdown(
        "summary.md",
        MarkdownSummary("Run", metadata={"status": "ok"}).render(),
    )

    assert json.loads(json_path.read_text()) == {"a": 1, "b": 2}
    assert jsonl_path.read_text() == '{"row":1}\n'
    assert md_path.read_text().startswith("# Run\n\n- status: `ok`")
