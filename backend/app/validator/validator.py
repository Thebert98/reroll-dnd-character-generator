"""The SRD rules validator — pure Python, no LLM.

Takes a merged CharacterSheet and returns a list of structured errors. Empty
list == legal character. This is the differentiator: it deterministically
rejects illegal combinations (e.g. "Druids can't learn Fireball") and its output
is stored on every ``generation_runs`` row and surfaced inline in the UI.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel

from ..models import CharacterSheet
from . import srd_data as srd


class ValidationError(BaseModel):
    field: str
    rule: str
    detail: str


def _val(sheet: CharacterSheet, field: str):
    return getattr(sheet, field).value


def validate(sheet: CharacterSheet) -> List[ValidationError]:
    errors: List[ValidationError] = []
    errors += _validate_class(sheet)
    errors += _validate_level(sheet)
    errors += _validate_abilities(sheet)
    errors += _validate_race(sheet)
    errors += _validate_background(sheet)
    errors += _validate_alignment(sheet)
    errors += _validate_spells(sheet)
    return errors


def validate_fields(
    sheet: CharacterSheet,
    field_names: list[str],
) -> List[ValidationError]:
    """Run the full validator and return only the errors whose ``field``
    is in the given list. Used by the per-group pipeline to scope the
    corrective retry loop to just the group that ran.

    Cross-field errors (e.g. proficiencies missing the background's skills)
    surface against whichever field the validator blames — which matches
    the group that owns that field in the GROUPS partition.
    """
    if not field_names:
        return []
    want = set(field_names)
    return [e for e in validate(sheet) if e.field in want]


def _validate_class(sheet: CharacterSheet) -> List[ValidationError]:
    cls = _val(sheet, "char_class")
    if cls and cls not in srd.CLASSES:
        return [
            ValidationError(
                field="char_class",
                rule="class_exists",
                detail=f"'{cls}' is not an SRD class.",
            )
        ]
    return []


def _validate_level(sheet: CharacterSheet) -> List[ValidationError]:
    level = _val(sheet, "level")
    if level is None:
        return []
    try:
        level = int(level)
    except (TypeError, ValueError):
        return [
            ValidationError(field="level", rule="level_range",
                            detail="Level must be an integer.")
        ]
    if not 1 <= level <= 20:
        return [
            ValidationError(field="level", rule="level_range",
                            detail=f"Level {level} is outside the legal range 1-20.")
        ]
    return []


def _validate_abilities(sheet: CharacterSheet) -> List[ValidationError]:
    stats = _val(sheet, "stats")
    if not stats:
        return []
    if not isinstance(stats, dict):
        return [
            ValidationError(field="stats", rule="stats_shape",
                            detail="Ability scores must be an object of six scores.")
        ]
    errors: List[ValidationError] = []
    for ab in srd.ABILITIES:
        if ab not in stats:
            errors.append(
                ValidationError(field="stats", rule="stats_complete",
                                detail=f"Missing ability score '{ab}'.")
            )
            continue
        score = stats[ab]
        if not isinstance(score, int) or not 3 <= score <= 20:
            errors.append(
                ValidationError(
                    field="stats", rule="ability_range",
                    detail=f"{ab.upper()} score {score} is outside 3-20.",
                )
            )
    return errors


def _validate_alignment(sheet: CharacterSheet) -> List[ValidationError]:
    alignment = _val(sheet, "alignment")
    if alignment and alignment not in srd.ALIGNMENTS:
        return [
            ValidationError(
                field="alignment", rule="alignment_exists",
                detail=f"'{alignment}' is not one of the nine SRD alignments.",
            )
        ]
    return []


def _validate_race(sheet: CharacterSheet) -> List[ValidationError]:
    race = _val(sheet, "race")
    if race and race not in srd.RACES:
        return [
            ValidationError(field="race", rule="race_exists",
                            detail=f"'{race}' is not an SRD race.")
        ]
    return []


def _validate_background(sheet: CharacterSheet) -> List[ValidationError]:
    bg = _val(sheet, "background")
    if bg and bg not in srd.BACKGROUNDS:
        return [
            ValidationError(field="background", rule="background_exists",
                            detail=f"'{bg}' is not an SRD background.")
        ]
    # If proficiencies are present, ensure the background's granted skills are included.
    if bg and bg in srd.BACKGROUNDS:
        profs = _val(sheet, "proficiencies") or []
        if isinstance(profs, list):
            missing = [p for p in srd.BACKGROUNDS[bg] if p not in profs]
            if missing and profs:  # only flag when proficiencies were actually set
                return [
                    ValidationError(
                        field="proficiencies", rule="background_grants_proficiencies",
                        detail=f"{bg} grants {', '.join(srd.BACKGROUNDS[bg])}; "
                               f"missing: {', '.join(missing)}.",
                    )
                ]
    return []


def _validate_spells(sheet: CharacterSheet) -> List[ValidationError]:
    cls = _val(sheet, "char_class")
    level = _val(sheet, "level") or 1
    spells = _val(sheet, "spells") or []
    errors: List[ValidationError] = []

    if not isinstance(spells, list):
        return [
            ValidationError(field="spells", rule="spells_shape",
                            detail="Spells must be a list of spell names.")
        ]
    if not cls or cls not in srd.CLASSES:
        return errors  # class validity handled elsewhere

    cls_info = srd.CLASSES[cls]
    # Non-casters may not have spells.
    if cls_info["caster"] == "none":
        if spells:
            errors.append(
                ValidationError(
                    field="spells", rule="non_caster_no_spells",
                    detail=f"{cls} is not a spellcaster and cannot know spells.",
                )
            )
        return errors

    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 1
    legal_list = srd.class_spell_list(cls)
    cap = srd.max_spell_level(cls, level)

    for name in spells:
        spell = srd.SPELLS.get(name)
        if spell is None:
            errors.append(
                ValidationError(field="spells", rule="spell_exists",
                                detail=f"'{name}' is not a known SRD spell.")
            )
            continue
        if name not in legal_list:
            errors.append(
                ValidationError(
                    field="spells", rule="spell_on_class_list",
                    detail=f"{cls}s can't learn {name} — it isn't on the {cls} spell list.",
                )
            )
            continue
        if spell["level"] > cap:
            errors.append(
                ValidationError(
                    field="spells", rule="spell_level_available",
                    detail=f"{name} is level {spell['level']}, but a level {level} "
                           f"{cls} can only cast up to level {cap} spells.",
                )
            )
    return errors
