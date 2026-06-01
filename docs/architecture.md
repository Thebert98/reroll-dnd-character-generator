# Architecture

```
React (Vite)  ──HTTP──>  FastAPI  ──>  Generation pipeline (plain Python)
   │                        │                │
   │                        │                ├─ analyze_intent
 Supabase Auth              │                ├─ retrieve_rules ──> pgvector
 (JWT)                      │                ├─ plan_fields
   │                        │                ├─ generate ──> LLM (structured output)
   └──> Supabase Postgres <─┘                └─ validate ──> SRD validator
        (RLS, pgvector)                              │
                                                     └──> trace written to generation_runs
```

## Request lifecycle

1. The browser authenticates with Supabase Auth and receives a JWT.
2. Every API call carries the JWT as a bearer token.
3. FastAPI verifies the JWT (`app/auth.py`) and builds a Supabase client scoped
   to that user, so Postgres Row Level Security enforces per-user isolation.
4. Reads/writes for characters, versions, and generation runs go through that
   scoped client. The shared SRD corpus is read-only to any authenticated user.

## The locked-field contract

Each field is `{ value, locked, source }`. The server only ever asks the LLM to
fill **unlocked** fields, and after the model responds it re-asserts the locked
values defensively (`merge_preserving_locks`) — the model is never trusted to
preserve them.

## Why no orchestration framework

The pipeline is a linear sequence of named Python functions with one retrieval
tool and no cycles or dynamic routing, so a graph framework (LangGraph) would
add dependency weight with no benefit. Every step appends to a `Trace` object
that becomes one `generation_runs` row — the basis for both the trace viewer and
the eval harness.
```
```
