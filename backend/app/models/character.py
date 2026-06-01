"""The character sheet schema — the single source of truth for both the API
and the LLM's structured output.

Every field carries three properties:
  * ``value``  — the field's content (shape varies per field)
  * ``locked`` — if True, the AI may not modify it; it is a hard constraint
  * ``source`` — the AI's reasoning for the chosen value (null until generated)
"""
from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field as PydField


class Field(BaseModel):
    value: Any = None
    locked: bool = False
    source: str | None = None


class Stats(BaseModel):
    """The six ability scores. Used to give the ``stats`` field a typed shape
    for validation and structured output; stored inside ``Field.value``."""
    str_: int = PydField(0, alias="str")
    dex: int = 0
    con: int = 0
    int_: int = PydField(0, alias="int")
    wis: int = 0
    cha: int = 0

    model_config = {"populate_by_name": True}


class CharacterSheet(BaseModel):
    name: Field = PydField(default_factory=Field)
    race: Field = PydField(default_factory=Field)
    char_class: Field = PydField(default_factory=Field)   # 'class' is reserved
    background: Field = PydField(default_factory=Field)
    alignment: Field = PydField(default_factory=Field)
    level: Field = PydField(default_factory=Field)        # int 1-20
    stats: Field = PydField(default_factory=Field)        # { str, dex, con, int, wis, cha }
    proficiencies: Field = PydField(default_factory=Field)
    spells: Field = PydField(default_factory=Field)       # [] for non-casters
    equipment: Field = PydField(default_factory=Field)
    backstory: Field = PydField(default_factory=Field)
    personality: Field = PydField(default_factory=Field)


# Canonical, ordered list of field names on the sheet.
SHEET_FIELDS: List[str] = list(CharacterSheet.model_fields.keys())


def empty_sheet() -> CharacterSheet:
    """A blank sheet with every field present, unlocked, and empty."""
    return CharacterSheet()


def sheet_from_dict(data: dict | None) -> CharacterSheet:
    """Build a CharacterSheet from a stored JSONB blob, tolerating partial or
    legacy shapes by filling in missing fields with empty ones."""
    data = data or {}
    normalized: dict[str, Any] = {}
    for fname in SHEET_FIELDS:
        raw = data.get(fname)
        if isinstance(raw, dict):
            normalized[fname] = Field(**raw)
        elif raw is None:
            normalized[fname] = Field()
        else:
            # Tolerate a bare value being stored without the wrapper.
            normalized[fname] = Field(value=raw)
    return CharacterSheet(**normalized)


def locked_field_names(sheet: CharacterSheet) -> List[str]:
    return [f for f in SHEET_FIELDS if getattr(sheet, f).locked]
