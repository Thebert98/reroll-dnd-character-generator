"""Prompt assembly and the JSON schema the model fills.

The model is asked to return *only the unlocked fields*, each as
``{ value, source }`` where ``source`` is its one-sentence reasoning.
"""
from __future__ import annotations

import json
from typing import List

from ..models import CharacterSheet, SHEET_FIELDS

SYSTEM = """You are an expert Dungeons & Dragons 5e character architect. You \
build characters that are legal under the SRD 5.1 rules and creatively coherent.

You are given a partially-filled character sheet. Some fields are LOCKED — these \
are hard constraints chosen by the user; treat them as both rules you must \
satisfy and creative inspiration. You must fill only the UNLOCKED fields \
requested of you. Never restate or change locked fields.

Rules you must respect:
- Ability scores are integers 3-20.
- Spells must be on the character's class spell list and within the levels the \
character can cast. Non-spellcasters have an empty spells list.
- Proficiencies must include those granted by the chosen background.
- Equipment must be plausible starting gear for the class and background.

Return ONLY the requested unlocked fields. For each field provide a `value` and \
a short `source` explaining your reasoning (one sentence)."""


def field_value_schema(field: str) -> dict:
    """The JSON shape of a single field's value, per field name."""
    if field == "level":
        return {"type": "integer", "minimum": 1, "maximum": 20}
    if field == "stats":
        return {
            "type": "object",
            "properties": {
                ab: {"type": "integer", "minimum": 3, "maximum": 20}
                for ab in ["str", "dex", "con", "int", "wis", "cha"]
            },
            "required": ["str", "dex", "con", "int", "wis", "cha"],
        }
    if field in ("proficiencies", "spells", "equipment"):
        return {"type": "array", "items": {"type": "string"}}
    return {"type": "string"}


def build_schema(unlocked: List[str]) -> dict:
    """JSON schema for the model output: one entry per unlocked field."""
    props = {
        f: {
            "type": "object",
            "properties": {
                "value": field_value_schema(f),
                "source": {"type": "string"},
            },
            "required": ["value", "source"],
        }
        for f in unlocked
    }
    return {"type": "object", "properties": props, "required": unlocked}


def build_corrective_user_prompt(
    sheet: CharacterSheet,
    failing_fields: List[str],
    validation_errors: list[dict],
    original_user_notes: str,
    chunks: list[dict] | None = None,
) -> str:
    """Build the prompt for a single corrective LLM call.

    Tells the model exactly what failed and asks for fixes scoped to the
    failing fields only. Everything else on the sheet stays as it was; the
    pipeline runs this on the merged sheet immediately after a group's
    first attempt failed validation.
    """
    locked = {
        f: getattr(sheet, f).value
        for f in SHEET_FIELDS
        if getattr(sheet, f).locked and getattr(sheet, f).value not in (None, "", [], {})
    }
    current = {
        f: getattr(sheet, f).value
        for f in failing_fields
        if getattr(sheet, f).value not in (None, "", [], {})
    }
    parts: list[str] = []
    parts.append(
        "Your previous output failed SRD validation. Fix ONLY the failing fields "
        "and keep every other field on the sheet exactly as it is."
    )
    parts.append("")
    parts.append("VALIDATION ERRORS (each is a fact you must satisfy):")
    parts.append(json.dumps(validation_errors, indent=2))
    parts.append("")
    parts.append("CURRENT VALUES OF THE FAILING FIELDS (the values you must revise):")
    parts.append(json.dumps(current, indent=2) if current else "(none set)")
    parts.append("")
    parts.append("LOCKED FIELDS (still hard constraints — do not change):")
    parts.append(json.dumps(locked, indent=2) if locked else "(none)")
    parts.append("")
    parts.append(f"FIELDS TO RETURN: {', '.join(failing_fields)}")
    if original_user_notes:
        parts.append("")
        parts.append(f"ORIGINAL USER NOTES / THEME: {original_user_notes}")
    if chunks:
        parts.append("")
        parts.append("RELEVANT SRD RULES (cite these; do not contradict them):")
        for c in chunks:
            section = c.get("section", "SRD")
            parts.append(f"[{section}] {c.get('text', c.get('content', ''))}")
    parts.append("")
    parts.append(
        "Return a JSON object with exactly the failing fields above, "
        "corrected so every listed validation error is resolved."
    )
    return "\n".join(parts)


def build_user_prompt(
    sheet: CharacterSheet,
    unlocked: List[str],
    user_notes: str,
    chunks: list[dict] | None = None,
    context: dict | None = None,
) -> str:
    locked = {
        f: getattr(sheet, f).value
        for f in SHEET_FIELDS
        if getattr(sheet, f).locked and getattr(sheet, f).value not in (None, "", [], {})
    }
    parts: list[str] = []
    parts.append("LOCKED FIELDS (hard constraints — do not change):")
    parts.append(json.dumps(locked, indent=2) if locked else "(none)")
    parts.append("")
    # Values produced by earlier nodes in the pipeline graph. They're not
    # locked at the sheet level, but for THIS LLM call they should be
    # treated as fixed context — the per-group split means each group has
    # its own scope; bleeding identity revisions into the mechanics group
    # would defeat the point.
    if context:
        non_empty = {
            k: v for k, v in context.items() if v not in (None, "", [], {})
        }
        if non_empty:
            parts.append(
                "ALREADY GENERATED (decided by an earlier step — use as context, do not change):"
            )
            parts.append(json.dumps(non_empty, indent=2))
            parts.append("")
    parts.append(f"FIELDS TO GENERATE (unlocked): {', '.join(unlocked)}")
    if user_notes:
        parts.append("")
        parts.append(f"USER NOTES / THEME: {user_notes}")
    if chunks:
        parts.append("")
        parts.append("RELEVANT SRD RULES (cite these; do not contradict them):")
        for c in chunks:
            section = c.get("section", "SRD")
            parts.append(f"[{section}] {c.get('text', c.get('content', ''))}")
    parts.append("")
    parts.append("Return a JSON object with exactly the unlocked fields above.")
    return "\n".join(parts)
