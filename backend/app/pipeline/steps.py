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
    """One structured-output LLM call. Returns the result and the prompt used."""
    schema = build_schema(plan)
    prompt = build_user_prompt(sheet, plan, user_notes, chunks)
    result = generate_structured(SYSTEM, prompt, schema, model=model)
    full_prompt = f"SYSTEM:\n{SYSTEM}\n\nUSER:\n{prompt}"
    return result, full_prompt


__all__ = [
    "Intent",
    "analyze_intent",
    "plan_fields",
    "generate_fields",
    "locked_value_summary",
]
