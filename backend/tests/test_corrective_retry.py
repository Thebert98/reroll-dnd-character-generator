"""Tests for the per-group corrective retry loop.

The pipeline calls one LLM per group. After each call, the validator runs
against the just-generated fields; if errors exist, the pipeline fires
one corrective LLM call and re-validates. These tests pin that behavior
by patching the stub provider to first emit a known-bad payload for the
mechanics group, then accept its own corrected output on the retry.
"""
from __future__ import annotations

import json

from app.models import sheet_from_dict
from app.pipeline import generate_character


def _empty_sheet():
    return sheet_from_dict({})


def _trace_step_names(trace) -> list[str]:
    return [s.name for s in trace.steps]


def _force_bad_proficiencies_then_correct(monkeypatch):
    """Patch the stub so the first mechanics call emits Acolyte proficiencies
    missing Insight + Religion; subsequent calls fall back to the original
    stub (which is SRD-aware enough to emit the right fix when re-asked).
    """
    from app.llm import stub_provider

    real_complete = stub_provider.complete
    state = {"bad_emitted": False}

    def fake_complete(*, system: str, user: str, schema: dict, model: str):
        # Only intercept the first mechanics call — recognized by the
        # presence of "proficiencies" in the schema's required list and
        # the bad_emitted flag being false.
        required = schema.get("required") or list(schema.get("properties", {}).keys())
        if (
            not state["bad_emitted"]
            and "proficiencies" in required
            and "stats" in required
        ):
            state["bad_emitted"] = True
            data = {
                "stats": {
                    "value": {
                        "str": 10,
                        "dex": 12,
                        "con": 14,
                        "int": 12,
                        "wis": 16,
                        "cha": 13,
                    },
                    "source": "forced bad output",
                },
                # Acolyte SHOULD grant Insight + Religion — emit Athletics
                # instead to trip the validator.
                "proficiencies": {
                    "value": ["Athletics"],
                    "source": "forced bad output",
                },
                "spells": {
                    "value": [],
                    "source": "forced bad output",
                },
            }
            return stub_provider.LLMResult(
                data=data,
                raw_text=json.dumps(data),
                input_tokens=len(user) // 4,
                output_tokens=len(json.dumps(data)) // 4,
                model="stub",
            )
        return real_complete(system=system, user=user, schema=schema, model=model)

    monkeypatch.setattr(stub_provider, "complete", fake_complete)


def test_pipeline_fires_corrective_when_mechanics_fails(monkeypatch):
    _force_bad_proficiencies_then_correct(monkeypatch)
    sheet = sheet_from_dict(
        {
            "char_class": {"value": "Cleric", "locked": True},
            "background": {"value": "Acolyte", "locked": True},
            "level": {"value": 3, "locked": True},
            "race": {"value": "Human", "locked": True},
        }
    )
    merged, trace = generate_character(sheet, "")
    names = _trace_step_names(trace)
    # Mechanics failed → corrective retry should have fired.
    assert "validate.mechanics" in names
    assert "correct.mechanics" in names
    assert "revalidate.mechanics" in names
    # The retry should have restored Acolyte's two granted skills.
    profs = merged.proficiencies.value or []
    assert "Insight" in profs
    assert "Religion" in profs


def test_pipeline_skips_corrective_when_group_validates(monkeypatch):
    # Clean run — the stub's deterministic baseline is SRD-legal for the
    # default character, so the corrective call should never fire.
    sheet = sheet_from_dict(
        {
            "char_class": {"value": "Fighter", "locked": True},
            "background": {"value": "Soldier", "locked": True},
            "level": {"value": 3, "locked": True},
            "race": {"value": "Human", "locked": True},
        }
    )
    _, trace = generate_character(sheet, "")
    names = _trace_step_names(trace)
    assert "validate.mechanics" in names
    # No correction needed — neither correct.* nor revalidate.* should appear.
    assert not any(n.startswith("correct.") for n in names)
    assert not any(n.startswith("revalidate.") for n in names)
