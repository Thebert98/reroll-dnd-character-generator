# Architecture

```
React (Vite)  ──HTTP──>  FastAPI  ──>  Generation pipeline (plain Python)
   │                        │                │
   │                        │                ├─ analyze_intent
 Supabase Auth              │                ├─ retrieve_rules ──> pgvector
 (JWT)                      │                ├─ plan_fields
   │                        │                │
   │                        │                ├─ generate.identity ──┐
   │                        │                │   validate.identity  │ ◄─ corrective
   │                        │                │   correct.identity?  │    retry loop
   │                        │                │                      │    (one shot
   │                        │                ├─ generate.mechanics ─┤     per group)
   │                        │                │   validate.mechanics │
   │                        │                │   correct.mechanics? │
   │                        │                │                      │
   │                        │                ├─ generate.narrative ─┤
   │                        │                │   validate.narrative │
   │                        │                │   correct.narrative? │
   │                        │                │                      │
   └──> Supabase Postgres <─┘                └─ validate (full sheet)
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

## Generation graph (per-group split + corrective retry)

The `generate` stage is split into three named groups (`identity`,
`mechanics`, `narrative`), each one structured-output LLM call scoped to
a subset of the sheet fields. After every group we run `validate_fields`
against just that group's plan; if it returns errors, the pipeline runs
one corrective LLM call seeded with the specific errors + the offending
current values + a fix-only-these-fields instruction, then re-validates.

- Bounded retry: at most one corrective call per group. Worst case: six
  LLM calls per `/generate` (3 groups × 2 attempts). Average case: three.
- Identity values produced by the first group ride into mechanics +
  narrative via an `ALREADY GENERATED` section in the prompt, so the
  later groups have full context even though the fields aren't locked.
- Locked fields stay locked across every group (`merge_preserving_locks`
  re-asserts on every merge).
- Each named step appends to a `Trace` object that becomes one
  `generation_runs` row — `generate.identity` / `validate.identity` /
  optionally `correct.identity` + `revalidate.identity`, repeated per
  group, ending with the full-sheet `validate` step.

## Why no orchestration framework

The pipeline is a directed acyclic flow of named Python functions with
one retrieval tool and bounded retries (no cycles, no dynamic routing),
so a graph framework (LangGraph) would add dependency weight with no
benefit. Native Python orchestration in `pipeline.py` carries the whole
graph in ~60 lines.
```
```
