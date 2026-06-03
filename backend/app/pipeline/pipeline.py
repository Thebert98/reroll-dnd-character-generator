"""The generation pipeline: graph-style group nodes with per-group validation.

    analyze_intent → retrieve_rules → plan_fields → [
        generate.identity  → validate.identity  → (correct.identity?)  →
        generate.mechanics → validate.mechanics → (correct.mechanics?) →
        generate.narrative → validate.narrative → (correct.narrative?)
    ] → validate

Each group is one structured-output LLM call scoped to a subset of the
sheet fields (identity / mechanics / narrative). After every group we
validate just that group's fields; if the validator objects, the next
PR adds a single corrective LLM call seeded with the errors. The flow
stays a DAG — bounded retries, no autonomous loops — so a graph
framework would add weight with no benefit. Each named step appends to
the Trace; the API signature is unchanged.
"""
from __future__ import annotations

import time
from typing import Callable

from ..models import CharacterSheet
from ..models.trace import Trace
from ..rag import build_retrieval_query
from ..validator import validate, validate_fields
from .merge import locked_value_summary, merge_preserving_locks
from .steps import (
    GROUPS,
    analyze_intent,
    generate_field_group,
    plan_fields,
)

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

    # 4. generate — one structured-output LLM call per group, validated
    # immediately so a later group's failure can't pollute earlier fields.
    merged = sheet
    raw_output: dict = {}
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost_usd = 0.0
    last_model = model or ""
    prompts: list[str] = []

    # Context dict bridges groups: identity's outputs become mechanics'
    # context so the LLM sees "char_class=Cleric, level=3" when picking
    # stats / proficiencies / spells, even though those fields are still
    # technically unlocked on the sheet.
    generated_context: dict = {}

    for group_name, group_fields in GROUPS:
        group_plan = [f for f in group_fields if f in intent.unlocked_fields]
        if not group_plan:
            continue

        t = time.perf_counter()
        result, prompt = generate_field_group(
            merged,
            retrieved_chunks,
            group_plan,
            user_notes,
            model,
            context=generated_context,
        )
        merged = merge_preserving_locks(merged, result.data)
        # Carry produced values forward for the next group.
        for fname, payload in result.data.items():
            if isinstance(payload, dict) and "value" in payload:
                generated_context[fname] = payload["value"]
            else:
                generated_context[fname] = payload
        raw_output.update(result.data)
        total_input_tokens += result.input_tokens
        total_output_tokens += result.output_tokens
        total_cost_usd += result.cost_usd or 0.0
        last_model = result.model
        prompts.append(f"--- {group_name} ---\n{prompt}")
        trace.add_step(
            f"generate.{group_name}",
            {
                "model": result.model,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "fields_returned": list(result.data.keys()),
            },
            _ms(t),
        )

        # Scope validation to the fields this group emitted so the corrective
        # retry loop (next PR) can target them without re-litigating the
        # earlier groups' choices.
        group_errors = [e.model_dump() for e in validate_fields(merged, group_plan)]
        trace.add_step(
            f"validate.{group_name}",
            {"error_count": len(group_errors), "errors": group_errors},
            0,
        )

    # 5. validate — full-sheet check is the final word reported to the API.
    t = time.perf_counter()
    errors = [e.model_dump() for e in validate(merged)]
    trace.add_step("validate", {"error_count": len(errors), "errors": errors}, _ms(t))

    trace.finish(
        model=last_model,
        prompt="\n\n".join(prompts),
        retrieved_chunks=retrieved_chunks,
        raw_output=raw_output,
        validation_errors=errors,
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
        cost_usd=total_cost_usd or None,
    )
    return merged, trace
