"""The generation pipeline: five named, separately-traced steps.

    analyze_intent → retrieve_rules → plan_fields → generate → validate

Each step appends to the Trace, which becomes one ``generation_runs`` row. The
flow is deterministic and linear (no cycles, no dynamic routing), so a graph
framework would add weight with no benefit. The public signature is unchanged
from earlier phases so the API and evals don't churn.
"""
from __future__ import annotations

import time
from typing import Callable

from ..models import CharacterSheet
from ..models.trace import Trace
from ..rag import build_retrieval_query
from ..validator import validate
from .merge import locked_value_summary, merge_preserving_locks
from .steps import analyze_intent, generate_fields, plan_fields

# A retriever takes a query string and returns SRD chunks. Injected so the
# pipeline stays decoupled from the database and testable in isolation.
Retriever = Callable[[str], list[dict]]


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def generate_character(
    sheet: CharacterSheet,
    user_notes: str = "",
    *,
    model: str | None = None,
    retrieved_chunks: list[dict] | None = None,
    retriever: Retriever | None = None,
) -> tuple[CharacterSheet, Trace]:
    trace = Trace.start(sheet)

    # 1. analyze_intent — deterministic; extract locks + infer theme.
    t = time.perf_counter()
    intent = analyze_intent(sheet, user_notes)
    trace.add_step(
        "analyze_intent",
        {
            "locked_fields": intent.locked_fields,
            "unlocked_fields": intent.unlocked_fields,
            "theme": intent.theme,
            "locked_values": locked_value_summary(sheet),
        },
        _ms(t),
    )

    # 2. retrieve_rules — hybrid search over the SRD corpus (if a retriever exists).
    query = build_retrieval_query(sheet, user_notes)
    if retrieved_chunks is None and retriever is not None:
        t = time.perf_counter()
        retrieved_chunks = retriever(query)
        trace.add_step(
            "retrieve_rules",
            {
                "query": query,
                "chunk_count": len(retrieved_chunks),
                "sections": [c.get("section") for c in retrieved_chunks],
            },
            _ms(t),
        )
    retrieved_chunks = retrieved_chunks or []

    # 3. plan_fields — order the unlocked fields by dependency (stats before spells).
    t = time.perf_counter()
    plan = plan_fields(sheet, intent)
    trace.add_step("plan_fields", {"order": plan}, _ms(t))

    if not plan:
        # Everything locked; nothing to generate. Still validate + trace.
        errors = [e.model_dump() for e in validate(sheet)]
        trace.add_step("validate", {"error_count": len(errors)}, 0)
        trace.finish(
            model=model or "none",
            retrieved_chunks=retrieved_chunks,
            validation_errors=errors,
        )
        return sheet, trace

    # 4. generate — one structured-output LLM call.
    t = time.perf_counter()
    result, prompt = generate_fields(sheet, retrieved_chunks, plan, user_notes, model)
    trace.add_step(
        "generate",
        {
            "model": result.model,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "fields_returned": list(result.data.keys()),
        },
        _ms(t),
    )
    merged = merge_preserving_locks(sheet, result.data)

    # 5. validate — pure-Python SRD rules check.
    t = time.perf_counter()
    errors = [e.model_dump() for e in validate(merged)]
    trace.add_step("validate", {"error_count": len(errors), "errors": errors}, _ms(t))

    trace.finish(
        model=result.model,
        prompt=prompt,
        retrieved_chunks=retrieved_chunks,
        raw_output=result.data,
        validation_errors=errors,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cost_usd=result.cost_usd,
    )
    return merged, trace
