#!/usr/bin/env python3
"""Eval harness: run a fixed set of cases through the generation pipeline and
report a pass rate. Run it on every prompt change; commit the summary so
improvement (or regression) is visible over time.

By default it uses the deterministic ``stub`` provider so it runs offline and
reproducibly (no API key). Point it at a real model to evaluate that model:

    python evals/run_evals.py                      # offline baseline (stub)
    LLM_PROVIDER=openai python evals/run_evals.py  # evaluate gpt-4o-mini
    LLM_PROVIDER=anthropic python evals/run_evals.py

Reports ``passed / total`` and lists failures with details.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent
sys.path.insert(0, str(BACKEND))


def _bootstrap_provider(provider: str | None) -> None:
    # Default to the offline stub unless the caller chose a real provider.
    os.environ.setdefault("LLM_PROVIDER", provider or "stub")
    if provider:
        os.environ["LLM_PROVIDER"] = provider


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", help="Override LLM_PROVIDER (stub|openai|anthropic)")
    ap.add_argument("--cases", type=Path, default=HERE / "cases.json")
    args = ap.parse_args()
    _bootstrap_provider(args.provider)

    # Imported after env is set so settings pick up the provider.
    from app.models import sheet_from_dict, locked_field_names  # noqa: E402
    from app.pipeline import generate_character  # noqa: E402
    from evals.assertions import ASSERTIONS  # noqa: E402

    cases = json.loads(args.cases.read_text())
    results = []
    passed = 0

    for case in cases:
        sheet = sheet_from_dict(case["input"])
        merged, trace = generate_character(sheet, case.get("notes", ""))
        ctx = {
            "input": sheet,
            "merged": merged,
            "trace": trace,
            "locked": locked_field_names(sheet),
        }
        failures = []
        for name in case["assertions"]:
            check = ASSERTIONS.get(name)
            if check is None:
                failures.append(f"{name}: unknown assertion")
                continue
            ok, msg = check(ctx)
            if not ok:
                failures.append(f"{name}: {msg}")
        case_passed = not failures
        passed += int(case_passed)
        results.append(
            {"name": case["name"], "passed": case_passed, "failures": failures}
        )

    total = len(cases)
    provider = os.environ["LLM_PROVIDER"]
    print(f"\nEval run · provider={provider} · {passed}/{total} passed\n")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        print(f"  {mark} {r['name']}")
        for f in r["failures"]:
            print(f"      - {f}")

    # Write a timestamped JSON (gitignored) and update the tracked summary.
    out_dir = HERE / "results"
    out_dir.mkdir(exist_ok=True)
    stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "timestamp": stamp,
        "provider": provider,
        "passed": passed,
        "total": total,
        "results": results,
    }
    (out_dir / f"{stamp}.json").write_text(json.dumps(payload, indent=2))
    _write_summary(payload)

    return 0 if passed == total else 1


def _write_summary(payload: dict) -> None:
    lines = [
        "# Eval results",
        "",
        f"Latest run: **{payload['passed']}/{payload['total']} passed** "
        f"(provider `{payload['provider']}`, {payload['timestamp']}).",
        "",
        "| Case | Result |",
        "|------|--------|",
    ]
    for r in payload["results"]:
        mark = "✅" if r["passed"] else "❌"
        detail = "" if r["passed"] else " — " + "; ".join(r["failures"])
        lines.append(f"| {r['name']} | {mark}{detail} |")
    lines.append("")
    lines.append(
        "Run with `python evals/run_evals.py` (offline `stub` baseline) or "
        "`LLM_PROVIDER=openai|anthropic python evals/run_evals.py` to evaluate a "
        "real model."
    )
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
