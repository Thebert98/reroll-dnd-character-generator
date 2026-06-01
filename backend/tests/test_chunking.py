from app.rag.chunking import parse_markdown_chunks

SAMPLE = """# Spells

## Fireball
A bright streak flashes from your pointing finger to a point you choose.
Each creature in a 20-foot-radius sphere must make a Dexterity saving throw.

## Cure Wounds
A creature you touch regains a number of hit points equal to 1d8 + your
spellcasting ability modifier.
"""


def test_chunks_split_per_heading():
    chunks = parse_markdown_chunks(SAMPLE, "spells")
    sections = [c["section"] for c in chunks]
    assert "Spells > Fireball" in sections
    assert "Spells > Cure Wounds" in sections


def test_section_breadcrumb_prepended_to_content():
    chunks = parse_markdown_chunks(SAMPLE, "spells")
    fireball = next(c for c in chunks if c["section"].endswith("Fireball"))
    assert fireball["content"].startswith("Spells > Fireball")
    assert "Dexterity saving throw" in fireball["content"]


def test_tiny_sections_dropped():
    # A heading with no meaningful body should not produce a chunk.
    chunks = parse_markdown_chunks("## Empty\n\n## Real\n" + "x" * 60, "f")
    assert all("Empty" not in c["section"] for c in chunks)
