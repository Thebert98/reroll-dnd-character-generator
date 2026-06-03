"""Tests for the per-group pipeline split.

The pipeline now runs three nodes (identity / mechanics / narrative), each
one LLM call validated immediately. These tests pin the new shape using
the stub provider so we don't need API keys in CI.
"""
from app.models import sheet_from_dict
from app.pipeline import generate_character


def _empty_sheet():
    return sheet_from_dict({})


def test_groups_each_produce_a_trace_step():
    sheet = _empty_sheet()
    merged, trace = generate_character(sheet, "")
    step_names = [s.name for s in trace.steps]
    # Three named generate steps, one per group.
    assert "generate.identity" in step_names
    assert "generate.mechanics" in step_names
    assert "generate.narrative" in step_names
    # Each one is followed by a per-group validate step.
    assert "validate.identity" in step_names
    assert "validate.mechanics" in step_names
    assert "validate.narrative" in step_names


def test_identity_context_flows_into_later_groups():
    sheet = _empty_sheet()
    merged, _trace = generate_character(sheet, "")
    # Identity group goes first and sets char_class. Mechanics + narrative
    # both depend on it — proficiencies + spells + equipment shouldn't be
    # empty just because the identity values weren't locked.
    assert merged.char_class.value
    assert merged.stats.value
    assert merged.proficiencies.value
    # Personality + backstory come from the narrative group; they should
    # be non-empty strings, not the empty Field default.
    assert merged.personality.value
    assert merged.backstory.value


def test_locked_fields_still_honored_in_grouped_flow():
    # Hard-lock a race; the identity group must not change it.
    sheet = sheet_from_dict(
        {
            "race": {"value": "Tiefling", "locked": True},
            "alignment": {"value": "Chaotic Neutral", "locked": True},
        }
    )
    merged, _trace = generate_character(sheet, "")
    assert merged.race.value == "Tiefling"
    assert merged.alignment.value == "Chaotic Neutral"
