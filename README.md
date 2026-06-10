# Re:Roll — Character Builder

> **Roll your legend. Build your story.**

An AI-assisted D&D character creator built around **locked-field iteration**:
fill in any subset of a character sheet, lock the fields you like, and the AI
regenerates the rest using your locked fields as hard constraints. Grounded in
SRD 5.1 rules via RAG, validated against those rules, and fully traceable.

> Build status: **shipped** — all six phases complete. Foundation → AI generation
> + SRD validator → version history + trace viewer → RAG → split pipeline + eval
> harness → polish (export, diff, share, rate limiting). See [`docs/`](docs/).

<!-- Add a demo GIF here once recorded, e.g. docs/demo.gif. The trace viewer
     (Sheet ▸ Trace tab) is the centerpiece to capture. -->
<!-- Live demo: <your Vercel URL> · API: <your Railway URL> -->

## Features

- **Locked-field iteration** — every field is `{ value, locked, source }`; lock
  what you love, regenerate the rest, never lose work. Locks are re-asserted
  server-side, never trusted to the model.
- **SRD validator** — pure-Python rules engine that rejects illegal characters
  (legal class/race/background, ability ranges, spell-list + spell-level rules).
- **Trace viewer** — per generation: locked constraints, retrieved SRD chunks
  with scores, the assembled prompt, raw model output, pass/fail validation, the
  five-step pipeline timeline, and token/cost/latency.
- **RAG grounding** — hybrid (semantic + full-text, RRF) retrieval over SRD 5.1,
  cited in the trace.
- **Eval harness** — 15 cases + an assertion library; `passed/total` with a
  committed baseline so prompt-change regressions are visible.
- **Polish** — JSON/PDF export, version history + restore + diff, read-only
  share links, per-user daily rate limiting, and "explain choices" (`source`).

## Why this exists

Most "AI generates a character" demos are thin chatbot wrappers. This one leads
with four differentiators:

1. **Locked-field iteration** as a first-class UX pattern — lock what you love,
   reroll the rest, never lose work.
2. A rules **validator** that rejects illegal characters (e.g. "Druids can't
   learn Fireball").
3. A **trace viewer** exposing retrieved context, prompts, token usage, and
   validation results per generation.
4. An **eval harness** that catches regressions when prompts change.

## Stack

| Layer        | Choice                                              |
|--------------|-----------------------------------------------------|
| Frontend     | React + Vite + Tailwind + Zustand                   |
| Backend      | FastAPI (Pydantic models double as the LLM schema)  |
| DB / Auth    | Supabase (Postgres + Auth + RLS, pgvector for RAG)  |
| LLM          | Anthropic / OpenAI behind one swappable adapter     |
| Deployment   | Vercel (frontend) · Railway (backend) · Supabase    |

## Repository layout

```
backend/    FastAPI app, Pydantic schema, pipeline, validator, evals
frontend/   React + Vite client (lock-toggle editor, trace viewer)
supabase/   SQL migrations (schema + RLS)
docs/       architecture notes
scripts/    one-off jobs (SRD ingestion)
```

## Local setup

### 1. Supabase
Create a project, then run the migrations in `supabase/migrations` in order
(SQL editor or `supabase db push`). Copy your project URL and keys.

### 2. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # fill in Supabase + LLM keys
uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd frontend
npm install
# set VITE_* vars in a .env.local (see ../.env.example)
npm run dev
```

## Eval results

The harness runs a fixed set of cases through the live pipeline and reports a
pass rate. The committed baseline uses a deterministic, SRD-aware `stub` provider
so it runs offline; point it at a real model to evaluate that model.

```bash
cd backend
python evals/run_evals.py                      # offline baseline (stub)
LLM_PROVIDER=openai python evals/run_evals.py  # evaluate gpt-4o-mini
```

Latest committed run: **19/19 passed** — full table in
[`backend/evals/RESULTS.md`](backend/evals/RESULTS.md). Coverage: pure scratch
generation, single/several locked fields, casters, non-casters, illegal
combinations the validator must catch, locked alignment / name / background
preservation, and fully-locked identity sheets.

## Architecture

See [`docs/architecture.md`](docs/architecture.md). The generation pipeline is
five named, separately-traced steps —
`analyze_intent → retrieve_rules → plan_fields → generate → validate` — kept
deterministic and linear (no graph framework, by design).

## Deployment

- **Frontend** → Vercel (`frontend/`, SPA rewrite in `vercel.json`).
- **Backend** → Railway (`backend/`, `railway.json` / `Procfile`).
- **DB/Auth** → Supabase: run `supabase/migrations/*.sql` in order; enable the
  `vector` extension; ingest the SRD with `scripts/ingest_srd.py`.

Set env vars per [`.env.example`](.env.example).

## Resume framing

> Built a D&D character generator with locked-field iteration: users lock any
> subset of fields and the AI regenerates the rest under SRD rule constraints.
> Includes a validation layer that rejects illegal combinations, a RAG pipeline
> grounding generations in CC-licensed SRD rules with citations, a trace viewer
> exposing retrieved context and token usage per generation, and an eval harness
> tracking prompt-change regressions. React, FastAPI, Supabase pgvector,
> structured outputs.

## Attribution

This product includes rules text from the **System Reference Document 5.1**
("SRD 5.1") by Wizards of the Coast LLC, available under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).
No content from the Player's Handbook or other copyrighted books is used.
