"""Phase-2 generation pipeline: a single linear pass.

    sheet ──> build prompt ──> LLM (structured) ──> merge (preserve locks)
          ──> validate ──> (sheet, trace)

Phase 5 splits this into named, separately-traced steps
(analyze_intent → retrieve_rules → plan_fields → generate → validate). The
public signature stays stable so the API and evals don't churn.
"""
from __future__ import annotations

from ..llm import generate_structured
from ..models import CharacterSheet
from ..models.trace import Trace
from ..validator import validate
from .merge import merge_preserving_locks, unlocked_field_names
from .prompt import SYSTEM, build_schema, build_user_prompt


def generate_character(
    sheet: CharacterSheet,
    user_notes: str = "",
    *,
    model: str | None = None,
    retrieved_chunks: list[dict] | None = None,
) -> tuple[CharacterSheet, Trace]:
    trace = Trace.start(sheet)

    unlocked = unlocked_field_names(sheet)
    if not unlocked:
        # Everything is locked; nothing to generate. Still validate + trace.
        errors = [e.model_dump() for e in validate(sheet)]
        trace.finish(model=model or "none", validation_errors=errors)
        return sheet, trace

    schema = build_schema(unlocked)
    prompt = build_user_prompt(sheet, unlocked, user_notes, retrieved_chunks)

    result = generate_structured(SYSTEM, prompt, schema, model=model)
    merged = merge_preserving_locks(sheet, result.data)
    errors = [e.model_dump() for e in validate(merged)]

    trace.finish(
        model=result.model,
        prompt=f"SYSTEM:\n{SYSTEM}\n\nUSER:\n{prompt}",
        retrieved_chunks=retrieved_chunks,
        raw_output=result.data,
        validation_errors=errors,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=result.cost_usd,
    )
    return merged, trace
