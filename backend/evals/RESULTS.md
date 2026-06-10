# Eval results

Latest run: **19/19 passed** (provider `stub`, 20260610T165243Z).

| Case | Result |
|------|--------|
| pure scratch generation | ✅ |
| single locked field: Druid | ✅ |
| several locked: Wizard 5 / High Elf | ✅ |
| caster: Cleric level 3 | ✅ |
| non-caster: Fighter level 4 | ✅ |
| illegal locked combo: Druid with Fireball | ✅ |
| level 5 druid, race locked to elf | ✅ |
| high level caster: Wizard 11 | ✅ |
| Sorcerer level 1 | ✅ |
| Bard level 2 | ✅ |
| Paladin level 5 (half caster) | ✅ |
| Ranger level 2 (half caster) | ✅ |
| Barbarian level 1 (non-caster) | ✅ |
| locked stats + class are preserved | ✅ |
| illegal locked combo: Fighter with Magic Missile | ✅ |
| locked alignment is preserved (Lawful Good Paladin) | ✅ |
| locked name survives generation | ✅ |
| locked background grants its skills (Acolyte Cleric) | ✅ |
| fully-locked identity sheet still generates mechanics + narrative | ✅ |

Run with `python evals/run_evals.py` (offline `stub` baseline) or `LLM_PROVIDER=openai|anthropic python evals/run_evals.py` to evaluate a real model.
