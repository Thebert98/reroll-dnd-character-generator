# Arcane Architect

An AI-assisted D&D character creator built around **locked-field iteration**:
fill in any subset of a character sheet, lock the fields you like, and the AI
regenerates the rest using your locked fields as hard constraints. Grounded in
SRD 5.1 rules via RAG, validated against those rules, and fully traceable.

> Build status: **Phase 1 — Foundation** (auth, schema, character CRUD, lock UI).
> Later phases add AI generation, the SRD validator, the trace viewer, RAG, and
> an eval harness. See [`docs/`](docs/) and the project plan.

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

## Attribution

This product includes rules text from the **System Reference Document 5.1**
("SRD 5.1") by Wizards of the Coast LLC, available under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/legalcode).
No content from the Player's Handbook or other copyrighted books is used.
