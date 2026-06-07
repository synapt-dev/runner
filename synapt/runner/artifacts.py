"""Artifact sinks for local files and future remote mirrors."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Protocol

from .hashing import canonical_json


class ArtifactSink(Protocol):
    """Minimal sink seam for local files, HF datasets, or future object stores."""

    def write_jsonl(self, relative_path: str | Path, records: Iterable[Any]) -> Path:
        """Write canonical JSONL records and return the concrete path."""

    def write_json(self, relative_path: str | Path, payload: Any) -> Path:
        """Write canonical JSON and return the concrete path."""

    def write_markdown(self, relative_path: str | Path, markdown: str) -> Path:
        """Write markdown and return the concrete path."""


@dataclass(frozen=True)
class JsonlWriter:
    path: Path

    def write(self, records: Iterable[Any]) -> Path:
        return write_jsonl(self.path, records)


@dataclass(frozen=True)
class MarkdownSummary:
    title: str
    lines: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        rendered = [f"# {self.title}", ""]
        if self.metadata:
            for key in sorted(self.metadata):
                rendered.append(f"- {key}: `{self.metadata[key]}`")
            rendered.append("")
        rendered.extend(self.lines)
        if rendered[-1:] != [""]:
            rendered.append("")
        return "\n".join(rendered)


@dataclass(frozen=True)
class LocalArtifactSink:
    root: Path

    def write_jsonl(self, relative_path: str | Path, records: Iterable[Any]) -> Path:
        return write_jsonl(self.root / relative_path, records)

    def write_json(self, relative_path: str | Path, payload: Any) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{canonical_json(payload)}\n", encoding="utf-8")
        return path

    def write_markdown(self, relative_path: str | Path, markdown: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        return path


def write_jsonl(path: Path, records: Iterable[Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(canonical_json(record))
            handle.write("\n")
    return path
