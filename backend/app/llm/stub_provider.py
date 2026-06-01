"""Deterministic, SRD-aware stub provider.

Not a real model — it produces rule-legal character fields from the curated SRD
data. Its purpose is twofold:
  * a reproducible **offline baseline** for the eval harness (CI without API keys);
  * a fast local provider for developing the pipeline/validator/UI.

Switch to a real model by setting LLM_PROVIDER=anthropic|openai; the eval harness
and pipeline are identical either way. The stub reads the locked fields out of
the assembled prompt so it respects the same constraints a real model would.
"""
from __future__ import annotations

import json

from ..validator import srd_data as srd
from .adapter import LLMResult

_STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
# Where each class wants its highest scores (priority order of abilities).
_STAT_PRIORITY = {
    "Barbarian": ["str", "con", "dex", "wis", "cha", "int"],
    "Bard": ["cha", "dex", "con", "wis", "int", "str"],
    "Cleric": ["wis", "con", "str", "dex", "cha", "int"],
    "Druid": ["wis", "con", "dex", "int", "cha", "str"],
    "Fighter": ["str", "con", "dex", "wis", "cha", "int"],
    "Monk": ["dex", "wis", "con", "str", "cha", "int"],
    "Paladin": ["str", "cha", "con", "wis", "dex", "int"],
    "Ranger": ["dex", "wis", "con", "str", "cha", "int"],
    "Rogue": ["dex", "con", "int", "wis", "cha", "str"],
    "Sorcerer": ["cha", "con", "dex", "wis", "int", "str"],
    "Warlock": ["cha", "con", "dex", "wis", "int", "str"],
    "Wizard": ["int", "con", "dex", "wis", "cha", "str"],
}


def _parse_locked(user: str) -> dict:
    """Pull the LOCKED FIELDS JSON object out of the assembled prompt."""
    marker = "LOCKED FIELDS"
    idx = user.find(marker)
    if idx == -1:
        return {}
    rest = user[idx:]
    start = rest.find("{")
    if start == -1:
        return {}
    depth, end = 0, -1
    for i, ch in enumerate(rest[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return {}
    try:
        return json.loads(rest[start : end + 1])
    except json.JSONDecodeError:
        return {}


def _stats_for(char_class: str) -> dict:
    order = _STAT_PRIORITY.get(char_class, srd.ABILITIES)
    return {ab: _STANDARD_ARRAY[order.index(ab)] for ab in srd.ABILITIES}


def _legal_spells(char_class: str, level: int) -> list[str]:
    cap = srd.max_spell_level(char_class, level)
    if cap < 0:
        return []
    pool = [
        name
        for name in sorted(srd.class_spell_list(char_class))
        if srd.SPELLS[name]["level"] <= cap
    ]
    # A small, deterministic, legal selection: a couple cantrips + a few spells.
    return pool[: min(len(pool), 4)]


def _value_for(field: str, locked: dict) -> object:
    char_class = locked.get("char_class") or "Fighter"
    level = locked.get("level") or 3
    try:
        level = int(level)
    except (TypeError, ValueError):
        level = 3
    background = locked.get("background") or "Soldier"

    if field == "name":
        return "Test Hero"
    if field == "race":
        return "Human"
    if field == "char_class":
        return "Fighter"
    if field == "background":
        return "Soldier"
    if field == "alignment":
        return "Neutral Good"
    if field == "level":
        return 3
    if field == "stats":
        return _stats_for(char_class)
    if field == "proficiencies":
        return list(srd.BACKGROUNDS.get(background, ["Athletics", "Perception"]))
    if field == "spells":
        return _legal_spells(char_class, level)
    if field == "equipment":
        return ["Leather armor", "Dagger", "Explorer's pack"]
    if field == "personality":
        return "Brave, curious, and loyal to companions."
    if field == "backstory":
        return "Raised in a quiet village, drawn to adventure after a fateful night."
    return ""


def complete(*, system: str, user: str, schema: dict, model: str) -> LLMResult:
    locked = _parse_locked(user)
    requested = schema.get("required") or list(schema.get("properties", {}).keys())

    # Background drives proficiencies, so honor a generated background when
    # proficiencies are also requested.
    data: dict = {}
    for field in requested:
        data[field] = {
            "value": _value_for(field, locked),
            "source": f"stub baseline value for {field}",
        }
    # If both background and proficiencies are generated, align them.
    if "proficiencies" in data and "background" in data:
        bg = data["background"]["value"]
        data["proficiencies"]["value"] = list(
            srd.BACKGROUNDS.get(bg, data["proficiencies"]["value"])
        )

    raw_text = json.dumps(data)
    return LLMResult(
        data=data,
        raw_text=raw_text,
        input_tokens=len(user) // 4,
        output_tokens=len(raw_text) // 4,
        model="stub",
    )
