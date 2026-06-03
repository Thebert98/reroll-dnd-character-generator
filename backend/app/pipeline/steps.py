"""The named, traceable pipeline steps.

Splitting the single generate call into ``analyze_intent → retrieve_rules →
plan_fields → generate → validate`` makes the pipeline honestly "agentic": named
steps with a retrieval tool, each logged to the trace. It stays deterministic
and linear — no autonomous loops, no cycles — so no graph framework is needed.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..llm import LLMResult, generate_structured
from ..models import CharacterSheet, SHEET_FIELDS
from .merge import locked_value_summary, unlocked_field_names
from .prompt import SYSTEM, build_schema, build_user_prompt

# Dependency-aware field ordering. Stats come before spells (spell choices depend
# on the casting stat); identity fields come first to anchor the theme.
FIELD_ORDER = [
    "name",
    "race",
    "char_class",
    "background",
    "alignment",
    "level",
    "stats",
    "proficiencies",
    "spells",
    "equipment",
    "personality",
    "backstory",
]

# ---------------------------------------------------------------------------
# Group split for the graph-style generation flow. Each group becomes one
# LLM call, validated immediately so a later group's failure can't pollute
# earlier fields. See pipeline.py for the orchestration.
# ---------------------------------------------------------------------------
IDENTITY_GROUP = ["name", "race", "char_class", "background", "alignment", "level"]
MECHANICS_GROUP = ["stats", "proficiencies", "spells"]
NARRATIVE_GROUP = ["equipment", "personality", "backstory"]

GROUPS: list[tuple[str, list[str]]] = [
    ("identity", IDENTITY_GROUP),
    ("mechanics", MECHANICS_GROUP),
    ("narrative", NARRATIVE_GROUP),
]


@dataclass
class Intent:
    locked_fields: list[str]
    unlocked_fields: list[str]
    theme: str


def analyze_intent(sheet: CharacterSheet, user_notes: str) -> Intent:
    """Cheap, deterministic. Extract locked/unlocked fields and infer a theme
    from the locked identity values plus user notes. (No LLM call in v1.)"""
    locked = [f for f in SHEET_FIELDS if getattr(sheet, f).locked]
    unlocked = unlocked_field_names(sheet)
    theme_bits: list[str] = []
    for f in ("char_class", "race", "background", "alignment"):
        v = getattr(sheet, f).value
        if v:
            theme_bits.append(str(v))
    if user_notes:
        theme_bits.append(user_notes)
    return Intent(
        locked_fields=locked,
        unlocked_fields=unlocked,
        theme=", ".join(theme_bits),
    )


def plan_fields(sheet: CharacterSheet, intent: Intent) -> list[str]:
    """Return the unlocked fields to fill, in dependency order."""
    return [f for f in FIELD_ORDER if f in intent.unlocked_fields]


def generate_fields(
    sheet: CharacterSheet,
    chunks: list[dict],
    plan: list[str],
    user_notes: str,
    model: str | None,
) -> tuple[LLMResult, str]:
    """One structured-output LLM call. Returns the result and the prompt used.

    Kept for backwards compatibility with anything still calling it directly;
    the pipeline now uses ``generate_field_group`` per group.
    """
    return generate_field_group(sheet, chunks, plan, user_notes, model)


def generate_field_group(
    sheet: CharacterSheet,
    chunks: list[dict],
    group_plan: list[str],
    user_notes: str,
    model: str | None,
    context: dict | None = None,
) -> tuple[LLMResult, str]:
    """One structured-output LLM call scoped to a single group's field list.

    ``context`` is a ``{field: value}`` dict of values produced by earlier
    graph nodes. They surface in the prompt's "ALREADY GENERATED" section so
    the LLM has the full picture without us having to flip the sheet's lock
    flags around between groups.
    """
    schema = build_schema(group_plan)
    prompt = build_user_prompt(sheet, group_plan, user_notes, chunks, context=context)
    result = generate_structured(SYSTEM, prompt, schema, model=model)
    full_prompt = f"SYSTEM:\n{SYSTEM}\n\nUSER:\n{prompt}"
    return result, full_prompt


__all__ = [
    "Intent",
    "analyze_intent",
    "plan_fields",
    "generate_fields",
    "generate_field_group",
    "locked_value_summary",
    "IDENTITY_GROUP",
    "MECHANICS_GROUP",
    "NARRATIVE_GROUP",
    "GROUPS",
]
