from app.models import sheet_from_dict
from app.pipeline import merge_preserving_locks, unlocked_field_names


def test_locked_fields_never_change():
    sheet = sheet_from_dict(
        {
            "char_class": {"value": "Druid", "locked": True},
            "race": {"value": "Elf", "locked": False},
        }
    )
    # Model tries to overwrite the locked class and fill race.
    raw = {
        "char_class": {"value": "Wizard", "source": "ignored"},
        "race": {"value": "Human", "source": "fits theme"},
    }
    merged = merge_preserving_locks(sheet, raw)
    assert merged.char_class.value == "Druid"  # lock held
    assert merged.race.value == "Human"        # unlocked field updated
    assert merged.race.source == "fits theme"


def test_unlocked_field_names_excludes_locked():
    sheet = sheet_from_dict(
        {
            "name": {"value": "Aria", "locked": True},
            "level": {"value": 1, "locked": False},
        }
    )
    names = unlocked_field_names(sheet)
    assert "name" not in names
    assert "level" in names


def test_bare_value_accepted():
    sheet = sheet_from_dict({"alignment": {"value": "", "locked": False}})
    merged = merge_preserving_locks(sheet, {"alignment": "Chaotic Good"})
    assert merged.alignment.value == "Chaotic Good"
