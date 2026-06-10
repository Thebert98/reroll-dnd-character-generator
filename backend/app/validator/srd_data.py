"""Curated SRD 5.1 reference data used by the rules validator.

This is a deliberately compact, hand-checked subset — enough to enforce the
high-value rules (legal classes/races/backgrounds, ability ranges, and "this
spell isn't on your class list / is too high level for you"). Phase 4 adds RAG
grounding over the *full* SRD; this table stays the authority for hard rules
because a validator must be deterministic, not retrieved.

All content is from the System Reference Document 5.1 (CC-BY-4.0).
"""
from __future__ import annotations

ABILITIES = ["str", "dex", "con", "int", "wis", "cha"]

# Proficiency bonus by character level (SRD, levels 1-20).
def proficiency_bonus(level: int) -> int:
    return 2 + (max(1, min(level, 20)) - 1) // 4


# ---------------------------------------------------------------------------
# Classes and their spellcasting profile.
#   caster: "full" | "half" | "third" | "none"
#   ability: spellcasting ability, or None
#   prepared: True if the class prepares spells (Cleric/Druid/Paladin/Wizard)
# ---------------------------------------------------------------------------
CLASSES: dict[str, dict] = {
    "Barbarian": {"caster": "none", "ability": None},
    "Bard": {"caster": "full", "ability": "cha", "prepared": False},
    "Cleric": {"caster": "full", "ability": "wis", "prepared": True},
    "Druid": {"caster": "full", "ability": "wis", "prepared": True},
    "Fighter": {"caster": "none", "ability": None},
    "Monk": {"caster": "none", "ability": None},
    "Paladin": {"caster": "half", "ability": "cha", "prepared": True},
    "Ranger": {"caster": "half", "ability": "wis", "prepared": False},
    "Rogue": {"caster": "none", "ability": None},
    "Sorcerer": {"caster": "full", "ability": "cha", "prepared": False},
    "Warlock": {"caster": "pact", "ability": "cha", "prepared": False},
    "Wizard": {"caster": "full", "ability": "int", "prepared": True},
}

# Full-caster spell slots per character level (index 0 == 1st-level slots).
FULL_CASTER_SLOTS: dict[int, list[int]] = {
    1: [2], 2: [3], 3: [4, 2], 4: [4, 3], 5: [4, 3, 2],
    6: [4, 3, 3], 7: [4, 3, 3, 1], 8: [4, 3, 3, 2], 9: [4, 3, 3, 3, 1],
    10: [4, 3, 3, 3, 2], 11: [4, 3, 3, 3, 2, 1], 12: [4, 3, 3, 3, 2, 1],
    13: [4, 3, 3, 3, 2, 1, 1], 14: [4, 3, 3, 3, 2, 1, 1],
    15: [4, 3, 3, 3, 2, 1, 1, 1], 16: [4, 3, 3, 3, 2, 1, 1, 1],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1], 18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1], 20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}


def max_spell_level(char_class: str, level: int) -> int:
    """Highest spell level the character can cast (0 == cantrips only)."""
    cls = CLASSES.get(char_class)
    if not cls or cls["caster"] == "none":
        return -1  # non-caster: no spells at all
    caster = cls["caster"]
    if caster == "full":
        slots = FULL_CASTER_SLOTS.get(max(1, min(level, 20)), [])
        return len(slots)
    if caster == "half":
        # Half casters start at level 2; effective slot level rounds down.
        eff = (level + 1) // 2 if level >= 2 else 0
        slots = FULL_CASTER_SLOTS.get(max(1, eff), []) if eff else []
        return len(slots)
    if caster == "pact":  # Warlock: pact magic, capped at 5th by level 9
        return min(5, (level + 1) // 2)
    return 0


# ---------------------------------------------------------------------------
# Spell registry: name -> { level, classes }. Level 0 == cantrip.
# A representative SRD subset spanning every caster class; enough to enforce
# class-list and spell-level rules and to catch the canonical illegal cases.
# ---------------------------------------------------------------------------
SPELLS: dict[str, dict] = {
    # Cantrips ---------------------------------------------------------------
    "Fire Bolt": {"level": 0, "classes": {"Sorcerer", "Wizard"}},
    "Ray of Frost": {"level": 0, "classes": {"Sorcerer", "Wizard"}},
    "Mage Hand": {"level": 0, "classes": {"Bard", "Sorcerer", "Warlock", "Wizard"}},
    "Prestidigitation": {"level": 0, "classes": {"Bard", "Sorcerer", "Warlock", "Wizard"}},
    "Sacred Flame": {"level": 0, "classes": {"Cleric"}},
    "Guidance": {"level": 0, "classes": {"Cleric", "Druid"}},
    "Druidcraft": {"level": 0, "classes": {"Druid"}},
    "Produce Flame": {"level": 0, "classes": {"Druid"}},
    "Shillelagh": {"level": 0, "classes": {"Druid"}},
    "Vicious Mockery": {"level": 0, "classes": {"Bard"}},
    "Eldritch Blast": {"level": 0, "classes": {"Warlock"}},
    "Light": {"level": 0, "classes": {"Bard", "Cleric", "Sorcerer", "Wizard"}},
    "Spare the Dying": {"level": 0, "classes": {"Cleric"}},
    "Thaumaturgy": {"level": 0, "classes": {"Cleric"}},
    "Resistance": {"level": 0, "classes": {"Cleric", "Druid"}},
    "Minor Illusion": {"level": 0, "classes": {"Bard", "Sorcerer", "Warlock", "Wizard"}},
    "Dancing Lights": {"level": 0, "classes": {"Bard", "Sorcerer", "Wizard"}},
    "Mending": {"level": 0, "classes": {"Bard", "Cleric", "Druid", "Sorcerer", "Wizard"}},
    "Chill Touch": {"level": 0, "classes": {"Sorcerer", "Warlock", "Wizard"}},
    "Poison Spray": {"level": 0, "classes": {"Druid", "Sorcerer", "Warlock", "Wizard"}},
    "Acid Splash": {"level": 0, "classes": {"Sorcerer", "Wizard"}},
    "Message": {"level": 0, "classes": {"Bard", "Sorcerer", "Wizard"}},
    # 1st level --------------------------------------------------------------
    "Magic Missile": {"level": 1, "classes": {"Sorcerer", "Wizard"}},
    "Shield": {"level": 1, "classes": {"Sorcerer", "Wizard"}},
    "Burning Hands": {"level": 1, "classes": {"Sorcerer", "Wizard"}},
    "Cure Wounds": {"level": 1, "classes": {"Bard", "Cleric", "Druid", "Paladin", "Ranger"}},
    "Healing Word": {"level": 1, "classes": {"Bard", "Cleric", "Druid"}},
    "Bless": {"level": 1, "classes": {"Cleric", "Paladin"}},
    "Entangle": {"level": 1, "classes": {"Druid"}},
    "Faerie Fire": {"level": 1, "classes": {"Bard", "Druid"}},
    "Thunderwave": {"level": 1, "classes": {"Bard", "Druid", "Sorcerer", "Wizard"}},
    "Hex": {"level": 1, "classes": {"Warlock"}},
    "Hunters Mark": {"level": 1, "classes": {"Ranger"}},
    "Guiding Bolt": {"level": 1, "classes": {"Cleric"}},
    "Detect Magic": {"level": 1, "classes": {"Bard", "Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Wizard"}},
    "Sleep": {"level": 1, "classes": {"Bard", "Sorcerer", "Wizard"}},
    "Charm Person": {"level": 1, "classes": {"Bard", "Druid", "Sorcerer", "Warlock", "Wizard"}},
    "Identify": {"level": 1, "classes": {"Bard", "Wizard"}},
    "Mage Armor": {"level": 1, "classes": {"Sorcerer", "Wizard"}},
    "Disguise Self": {"level": 1, "classes": {"Bard", "Sorcerer", "Wizard"}},
    "Sanctuary": {"level": 1, "classes": {"Cleric"}},
    "Inflict Wounds": {"level": 1, "classes": {"Cleric"}},
    "Shield of Faith": {"level": 1, "classes": {"Cleric", "Paladin"}},
    "Detect Evil and Good": {"level": 1, "classes": {"Cleric", "Paladin"}},
    "Bane": {"level": 1, "classes": {"Bard", "Cleric"}},
    "Command": {"level": 1, "classes": {"Cleric", "Paladin"}},
    "Goodberry": {"level": 1, "classes": {"Druid", "Ranger"}},
    "Speak with Animals": {"level": 1, "classes": {"Bard", "Druid", "Ranger"}},
    "Protection from Evil and Good": {"level": 1, "classes": {"Cleric", "Paladin", "Warlock", "Wizard"}},
    "Divine Favor": {"level": 1, "classes": {"Paladin"}},
    "Heroism": {"level": 1, "classes": {"Bard", "Paladin"}},
    # 2nd level --------------------------------------------------------------
    "Misty Step": {"level": 2, "classes": {"Sorcerer", "Warlock", "Wizard"}},
    "Scorching Ray": {"level": 2, "classes": {"Sorcerer", "Wizard"}},
    "Spiritual Weapon": {"level": 2, "classes": {"Cleric"}},
    "Hold Person": {"level": 2, "classes": {"Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"}},
    "Moonbeam": {"level": 2, "classes": {"Druid"}},
    "Lesser Restoration": {"level": 2, "classes": {"Bard", "Cleric", "Druid", "Paladin", "Ranger"}},
    "Aid": {"level": 2, "classes": {"Cleric", "Paladin"}},
    "Pass without Trace": {"level": 2, "classes": {"Druid", "Ranger"}},
    "Prayer of Healing": {"level": 2, "classes": {"Cleric"}},
    "See Invisibility": {"level": 2, "classes": {"Bard", "Sorcerer", "Wizard"}},
    "Silence": {"level": 2, "classes": {"Bard", "Cleric", "Ranger"}},
    "Web": {"level": 2, "classes": {"Sorcerer", "Wizard"}},
    "Zone of Truth": {"level": 2, "classes": {"Bard", "Cleric", "Paladin"}},
    "Invisibility": {"level": 2, "classes": {"Bard", "Sorcerer", "Warlock", "Wizard"}},
    "Calm Emotions": {"level": 2, "classes": {"Bard", "Cleric"}},
    "Magic Weapon": {"level": 2, "classes": {"Paladin", "Wizard"}},
    "Spike Growth": {"level": 2, "classes": {"Druid", "Ranger"}},
    "Levitate": {"level": 2, "classes": {"Sorcerer", "Wizard"}},
    # 3rd level --------------------------------------------------------------
    "Fireball": {"level": 3, "classes": {"Sorcerer", "Wizard"}},
    "Counterspell": {"level": 3, "classes": {"Sorcerer", "Warlock", "Wizard"}},
    "Fly": {"level": 3, "classes": {"Sorcerer", "Warlock", "Wizard"}},
    "Call Lightning": {"level": 3, "classes": {"Druid"}},
    "Dispel Magic": {"level": 3, "classes": {"Bard", "Cleric", "Druid", "Paladin", "Sorcerer", "Warlock", "Wizard"}},
    "Revivify": {"level": 3, "classes": {"Cleric", "Paladin"}},
    "Spirit Guardians": {"level": 3, "classes": {"Cleric"}},
    "Beacon of Hope": {"level": 3, "classes": {"Cleric"}},
    "Bestow Curse": {"level": 3, "classes": {"Bard", "Cleric", "Wizard"}},
    "Daylight": {"level": 3, "classes": {"Cleric", "Druid", "Paladin", "Ranger", "Sorcerer", "Wizard"}},
    "Lightning Bolt": {"level": 3, "classes": {"Sorcerer", "Wizard"}},
    "Mass Healing Word": {"level": 3, "classes": {"Cleric"}},
    "Tongues": {"level": 3, "classes": {"Bard", "Cleric", "Sorcerer", "Warlock", "Wizard"}},
    "Conjure Animals": {"level": 3, "classes": {"Druid", "Ranger"}},
    "Plant Growth": {"level": 3, "classes": {"Bard", "Druid", "Ranger"}},
    "Slow": {"level": 3, "classes": {"Sorcerer", "Wizard"}},
    # 4th-5th level (samples for higher-level characters) --------------------
    "Polymorph": {"level": 4, "classes": {"Bard", "Druid", "Sorcerer", "Wizard"}},
    "Ice Storm": {"level": 4, "classes": {"Druid", "Sorcerer", "Wizard"}},
    "Greater Invisibility": {"level": 4, "classes": {"Bard", "Sorcerer", "Wizard"}},
    "Banishment": {"level": 4, "classes": {"Cleric", "Paladin", "Sorcerer", "Warlock", "Wizard"}},
    "Death Ward": {"level": 4, "classes": {"Cleric", "Paladin"}},
    "Wall of Fire": {"level": 4, "classes": {"Druid", "Sorcerer", "Wizard"}},
    "Cone of Cold": {"level": 5, "classes": {"Sorcerer", "Wizard"}},
    "Mass Cure Wounds": {"level": 5, "classes": {"Bard", "Cleric", "Druid"}},
    "Flame Strike": {"level": 5, "classes": {"Cleric"}},
    "Hold Monster": {"level": 5, "classes": {"Bard", "Sorcerer", "Warlock", "Wizard"}},
    "Wall of Force": {"level": 5, "classes": {"Wizard"}},
    "Raise Dead": {"level": 5, "classes": {"Bard", "Cleric", "Paladin"}},
}


def class_spell_list(char_class: str) -> set[str]:
    return {name for name, d in SPELLS.items() if char_class in d["classes"]}


# ---------------------------------------------------------------------------
# Races: ability score increases. (SRD subset.)
# ---------------------------------------------------------------------------
RACES: dict[str, dict[str, int]] = {
    "Hill Dwarf": {"con": 2, "wis": 1},
    "Mountain Dwarf": {"con": 2, "str": 2},
    "High Elf": {"dex": 2, "int": 1},
    "Wood Elf": {"dex": 2, "wis": 1},
    "Elf": {"dex": 2},
    "Dwarf": {"con": 2},
    "Lightfoot Halfling": {"dex": 2, "cha": 1},
    "Halfling": {"dex": 2},
    "Human": {"str": 1, "dex": 1, "con": 1, "int": 1, "wis": 1, "cha": 1},
    "Dragonborn": {"str": 2, "cha": 1},
    "Gnome": {"int": 2},
    "Half-Elf": {"cha": 2},
    "Half-Orc": {"str": 2, "con": 1},
    "Tiefling": {"int": 1, "cha": 2},
}

# ---------------------------------------------------------------------------
# Alignments: the nine SRD alignments + the abbreviated "Neutral" form.
# Stored canonically (e.g. "Chaotic Good") on the sheet.
# ---------------------------------------------------------------------------
ALIGNMENTS: set[str] = {
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
}

# ---------------------------------------------------------------------------
# Backgrounds: granted skill proficiencies. (SRD subset.)
# ---------------------------------------------------------------------------
BACKGROUNDS: dict[str, list[str]] = {
    "Acolyte": ["Insight", "Religion"],
    "Criminal": ["Deception", "Stealth"],
    "Folk Hero": ["Animal Handling", "Survival"],
    "Noble": ["History", "Persuasion"],
    "Sage": ["Arcana", "History"],
    "Soldier": ["Athletics", "Intimidation"],
    "Charlatan": ["Deception", "Sleight of Hand"],
    "Entertainer": ["Acrobatics", "Performance"],
    "Guild Artisan": ["Insight", "Persuasion"],
    "Hermit": ["Medicine", "Religion"],
    "Outlander": ["Athletics", "Survival"],
    "Urchin": ["Sleight of Hand", "Stealth"],
}
