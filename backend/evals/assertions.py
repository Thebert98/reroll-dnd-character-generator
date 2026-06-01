"""Assertion library for the eval harness.

Each assertion takes a context dict ``{input, merged, trace, locked}`` and
returns ``(ok: bool, message: str)``.
"""
from __future__ import annotations

from typing import Callable

from app.models import CharacterSheet
from app.validator import srd_data as srd

Context = dict
Assertion = Callable[[Context], tuple[bool, str]]


def _v(sheet: CharacterSheet, field: str):
    return getattr(sheet, field).value


def validator_passes(ctx: Context):
    errs = ctx["trace"].validation_errors
    return (len(errs) == 0, f"{len(errs)} validation error(s): {errs}")


def validator_catches_error(ctx: Context):
    errs = ctx["trace"].validation_errors
    return (len(errs) > 0, "expected at least one validation error, got none")


def locked_fields_unchanged(ctx: Context):
    original: CharacterSheet = ctx["input"]
    merged: CharacterSheet = ctx["merged"]
    for f in ctx["locked"]:
        if _v(merged, f) != _v(original, f):
            return (False, f"locked field '{f}' changed: "
                           f"{_v(original, f)!r} -> {_v(merged, f)!r}")
    return (True, "")


def all_unlocked_filled(ctx: Context):
    merged: CharacterSheet = ctx["merged"]
    original: CharacterSheet = ctx["input"]
    for f in CharacterSheet.model_fields:
        if getattr(original, f).locked:
            continue
        val = _v(merged, f)
        # 'spells' may legitimately be empty for non-casters.
        if f == "spells":
            continue
        if val in (None, "", [], {}):
            return (False, f"unlocked field '{f}' was not filled")
    return (True, "")


def spells_are_class_legal(ctx: Context):
    merged: CharacterSheet = ctx["merged"]
    cls = _v(merged, "char_class")
    spells = _v(merged, "spells") or []
    if cls not in srd.CLASSES:
        return (True, "")
    legal = srd.class_spell_list(cls)
    bad = [s for s in spells if s not in legal]
    return (not bad, f"non-{cls} spells present: {bad}")


def spells_within_cap(ctx: Context):
    merged: CharacterSheet = ctx["merged"]
    cls = _v(merged, "char_class")
    level = _v(merged, "level") or 1
    spells = _v(merged, "spells") or []
    if cls not in srd.CLASSES:
        return (True, "")
    cap = srd.max_spell_level(cls, int(level))
    over = [s for s in spells if srd.SPELLS.get(s, {}).get("level", 0) > cap]
    return (not over, f"spells above castable level {cap}: {over}")


def caster_has_spells(ctx: Context):
    merged: CharacterSheet = ctx["merged"]
    cls = _v(merged, "char_class")
    spells = _v(merged, "spells") or []
    if cls in srd.CLASSES and srd.CLASSES[cls]["caster"] == "none":
        return (True, "")
    return (len(spells) > 0, f"{cls} caster has no spells")


def non_caster_has_no_spells(ctx: Context):
    merged: CharacterSheet = ctx["merged"]
    cls = _v(merged, "char_class")
    spells = _v(merged, "spells") or []
    if cls in srd.CLASSES and srd.CLASSES[cls]["caster"] != "none":
        return (True, "")
    return (len(spells) == 0, f"non-caster {cls} has spells: {spells}")


ASSERTIONS: dict[str, Assertion] = {
    "validator_passes": validator_passes,
    "validator_catches_error": validator_catches_error,
    "locked_fields_unchanged": locked_fields_unchanged,
    "all_unlocked_filled": all_unlocked_filled,
    "spells_are_class_legal": spells_are_class_legal,
    "spells_within_cap": spells_within_cap,
    "caster_has_spells": caster_has_spells,
    "non_caster_has_no_spells": non_caster_has_no_spells,
}
