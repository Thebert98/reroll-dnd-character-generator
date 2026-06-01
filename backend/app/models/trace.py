"""The Trace object: accumulates everything about one generation and serializes
to a ``generation_runs`` row. Written on every generation, success or failure —
it powers both the trace viewer and the eval harness.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .character import CharacterSheet, locked_field_names


@dataclass
class PipelineStep:
    """One named pipeline step, for the phase-5 split pipeline."""
    name: str
    detail: dict[str, Any]
    duration_ms: int


@dataclass
class Trace:
    input_snapshot: dict
    locked_fields: list[str]
    model: str = ""
    retrieved_chunks: list[dict] | None = None
    prompt: str | None = None
    raw_output: dict | None = None
    validation_errors: list[dict] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    steps: list[PipelineStep] = field(default_factory=list)
    _t0: float = field(default_factory=time.perf_counter)
    latency_ms: int = 0

    @classmethod
    def start(cls, sheet: CharacterSheet) -> "Trace":
        return cls(
            input_snapshot=sheet.model_dump(by_alias=True),
            locked_fields=locked_field_names(sheet),
        )

    def add_step(self, name: str, detail: dict[str, Any], duration_ms: int) -> None:
        self.steps.append(PipelineStep(name=name, detail=detail, duration_ms=duration_ms))

    def finish(
        self,
        *,
        model: str,
        prompt: str | None = None,
        retrieved_chunks: list[dict] | None = None,
        raw_output: dict | None = None,
        validation_errors: list[dict] | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> "Trace":
        self.model = model
        self.prompt = prompt
        self.retrieved_chunks = retrieved_chunks
        self.raw_output = raw_output
        self.validation_errors = validation_errors or []
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cost_usd = cost_usd
        self.latency_ms = int((time.perf_counter() - self._t0) * 1000)
        return self

    def to_run_row(self, character_id: str, version_id: str | None = None) -> dict:
        """Shape this trace as a row for the ``generation_runs`` table."""
        return {
            "character_id": character_id,
            "version_id": version_id,
            "input_snapshot": self.input_snapshot,
            "locked_fields": self.locked_fields,
            "retrieved_chunks": self.retrieved_chunks,
            "prompt": self.prompt,
            "model": self.model,
            "raw_output": self.raw_output,
            "validation_errors": self.validation_errors,
            "latency_ms": self.latency_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
        }
