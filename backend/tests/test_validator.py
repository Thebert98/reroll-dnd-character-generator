from app.models import sheet_from_dict
from app.validator import validate


def _sheet(**fields):
    return sheet_from_dict({k: {"value": v, "locked": False} for k, v in fields.items()})


def test_legal_low_level_druid_passes():
    sheet = _sheet(
        char_class="Druid",
        level=3,
        race="Wood Elf",
        background="Hermit",
        stats={"str": 10, "dex": 14, "con": 13, "int": 12, "wis": 16, "cha": 8},
        spells=["Druidcraft", "Entangle", "Moonbeam"],
        proficiencies=["Medicine", "Religion"],
    )
    assert validate(sheet) == []


def test_druid_cannot_learn_fireball():
    sheet = _sheet(char_class="Druid", level=5, spells=["Fireball"])
    rules = {e.rule for e in validate(sheet)}
    assert "spell_on_class_list" in rules


def test_non_caster_with_spells_fails():
    sheet = _sheet(char_class="Fighter", level=3, spells=["Magic Missile"])
    rules = {e.rule for e in validate(sheet)}
    assert "non_caster_no_spells" in rules


def test_spell_level_too_high_for_level():
    # A level-1 wizard cannot cast Fireball (3rd level).
    sheet = _sheet(char_class="Wizard", level=1, spells=["Fireball"])
    rules = {e.rule for e in validate(sheet)}
    assert "spell_level_available" in rules


def test_ability_out_of_range():
    sheet = _sheet(
        char_class="Fighter",
        level=1,
        stats={"str": 25, "dex": 14, "con": 13, "int": 12, "wis": 10, "cha": 8},
    )
    rules = {e.rule for e in validate(sheet)}
    assert "ability_range" in rules


def test_unknown_class_and_race():
    sheet = _sheet(char_class="Jedi", race="Wookiee", level=1)
    rules = {e.rule for e in validate(sheet)}
    assert "class_exists" in rules
    assert "race_exists" in rules


def test_unknown_spell_flagged():
    sheet = _sheet(char_class="Wizard", level=5, spells=["Avada Kedavra"])
    rules = {e.rule for e in validate(sheet)}
    assert "spell_exists" in rules


def test_level_out_of_range():
    sheet = _sheet(char_class="Wizard", level=25)
    rules = {e.rule for e in validate(sheet)}
    assert "level_range" in rules
