"""Merge model output back into the sheet while defensively preserving locks.

The model is *asked* to return only unlocked fields, but we never trust it to
respect that — locked fields are re-asserted from the original sheet here.
"""
from __future__ import annotations

from typing import List

from ..models import CharacterSheet, Field, SHEET_FIELDS


def unlocked_field_names(sheet: CharacterSheet) -> List[str]:
    return [f for f in SHEET_FIELDS if not getattr(sheet, f).locked]


def merge_preserving_locks(original: CharacterSheet, raw: dict) -> CharacterSheet:
    """Return a new sheet where unlocked fields take the model's values and
    locked fields keep their original values no matter what the model returned.

    ``raw`` may be either ``{field: value}`` or ``{field: {value, source}}``.
    """
    merged = original.model_copy(deep=True)
    for fname in SHEET_FIELDS:
        field: Field = getattr(merged, fname)
        if field.locked:
            continue  # hard constraint — ignore any model output for this field
        if fname not in raw:
            continue
        produced = raw[fname]
        if isinstance(produced, dict) and "value" in produced:
            field.value = produced.get("value")
            field.source = produced.get("source")
        else:
            field.value = produced
        setattr(merged, fname, field)
    return merged
