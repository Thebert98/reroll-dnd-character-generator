# CLAUDE.md — Re:Roll orientation

Quick start for an AI assistant (or human reviewer) landing in this repo.

## What this project is

**Re:Roll** is an AI-assisted D&D 5e character creator. The flagship UX is
**locked-field iteration**: every field on the sheet is `{ value, locked, source }`,
and the model only ever fills *unlocked* fields. Locks are re-asserted server-side
after the LLM responds — the model is never trusted to preserve them.

Reads as a single-page React app talking to a FastAPI backend, with Supabase
Postgres + Auth + pgvector behind it. The full SRD 5.1 corpus is RAG'd and a
pure-Python validator gates every generation.

## Repo layout

```
backend/        FastAPI app + pipeline + validator + evals
  app/
    api/        CRUD + generate + versions + traces + share + export routes
    pipeline/   analyze_intent → retrieve_rules → plan_fields → generate.{identity,mechanics,narrative} → validate
    validator/  pure-Python SRD 5.1 rules engine + curated reference data
    rag/        embeddings + hybrid (semantic + full-text RRF) retrieval
    llm/        provider adapters (Anthropic, OpenAI, deterministic stub)
    models/     Pydantic schemas (CharacterSheet, Trace)
  tests/        pytest — pinned to LLM_PROVIDER=stub via conftest autouse
  evals/        cases.json + assertions.py + run_evals.py
frontend/       React + Vite + Tailwind + Zustand
supabase/       SQL migrations (schema + RLS + hybrid_search RPC)
docs/           architecture.md + branding.md
scripts/        SRD ingestion
.github/        CI workflow
```

## Critical invariants (don't break these)

- **Locked fields never change between input and output.** `merge_preserving_locks`
  in `backend/app/pipeline/merge.py` is the hard guard. Tested in
  `tests/test_merge.py` and exercised by ~6 of the eval cases.
- **Validation is server-side and deterministic.** The validator must remain a
  pure function of the sheet (no LLM calls, no I/O). It's the differentiator.
- **The pipeline graph is documented in `docs/architecture.md`.** It's a DAG with
  bounded retries (one corrective LLM call per group). No autonomous loops, no
  LangGraph dependency.

## How to make changes safely

1. **Run the harness.** `cd backend && pytest -q && python evals/run_evals.py`
   should print green before and after every change. Default `LLM_PROVIDER=stub`
   keeps it offline.
2. **Build the frontend.** `cd frontend && npm run build` is the type-check gate;
   there are no Vitest tests yet.
3. **Look at the trace, not just the response.** Every `/generate` writes a
   `generation_runs` row with the locked constraints, retrieved chunks, full
   prompt, raw output, validator errors, per-step timings, and token/cost.
4. **Schema changes go through migrations**, not ad-hoc DDL.

## Common pitfalls

- Don't add a backend field without updating: the Pydantic schema
  (`models/character.py`), the prompt builder, the validator, the GROUPS
  partition in `pipeline/steps.py`, the relevant evals, and the frontend type.
- Don't bypass the lock guard with "convenience" code paths. The whole product
  is the lock guard.
- Don't echo upstream exception detail back to API clients (see `auth.py` for the
  pattern: chain the cause with `from exc` for server logs, return a flat
  message to the client).

## Where to start reading

- `backend/app/pipeline/pipeline.py` — the orchestration in one file.
- `backend/app/pipeline/merge.py` — the lock guard.
- `backend/app/validator/validator.py` — the rules engine.
- `frontend/src/components/CharacterEditor.tsx` — the editor + lock toggle + trace tab entry point.
- `frontend/src/components/TraceViewer.tsx` — the demo centerpiece.

## Plan files

There is no `PLAN.md` in this repo. The shipped scope is documented in
`README.md` and `docs/architecture.md`. The session journal lives in
`SESSION.md` (local-only by `.gitignore`). The Fable audit pass that produced
`AUDIT.md` followed those as the spec.
