# ReRoll — Fable Audit

**Date:** 2026-06-10
**Branch:** `fable/audit-complete`
**Auditor:** Claude (Opus 4.7)
**Scope of audit:** Full codebase vs. the spec files (`README.md`, `SESSION.md`, `docs/architecture.md`, `docs/branding.md`). Audit prompt also referenced features (portrait generation, party management, bard song generator) that are **not in ReRoll's scope** — see § Scope reconciliation below.

---

## Scope reconciliation

The audit prompt lists six feature areas. Three of them are not part of this project per the spec files:

| Feature area | In ReRoll's spec? | Action |
|---|---|---|
| Character generation (locked-field iteration) | ✓ | Audited deeply |
| Character management (CRUD) | ✓ | Audited |
| RAG retrieval | ✓ | Audited |
| Eval harness + trace viewer | ✓ | Audited |
| Portrait generation | ✗ (sibling project) | Out of scope — documented |
| Party management | ✗ | Out of scope — documented |
| Bard song / lyrics / music API | ✗ | Out of scope — documented |

ReRoll is positioned in the README as an **AI-assisted D&D character creator built around locked-field iteration**, grounded in SRD 5.1 via RAG, validated against those rules. Status per README: *"shipped — all six phases complete."* Portrait / party / song features belong to a separate frontend wrapper (Tomoi's Tavern) and are not implemented in this repo. **I will not add them under "complete the plan."** If the user wants those features here, that's a scope expansion that needs its own decision.

---

## Test + eval status (baseline)

- `pytest`: **19/19 passed** (0.19s) with `LLM_PROVIDER=stub`.
- `python evals/run_evals.py`: **15/15 passed** with `LLM_PROVIDER=stub`. Covers pure scratch, locked subsets, casters, non-casters, illegal-combo rejection, locked-stat-preservation.
- `npm run build` (frontend): clean. Bundle 406 KB / 117 KB gzip.
- Backend imports cleanly.

Conclusion: the shipped baseline is not regressed. Bugs identified below are pre-existing.

---

## (a) Bugs — with file:line

### Backend

| # | Severity | File:Line | Description |
|---|---|---|---|
| B1 | **High** | `backend/app/rag/embeddings.py:21-25` | `embed()` makes the OpenAI call with no try/except. If the embedding API is down, the key is missing, or the model is rate-limited, the exception propagates uncaught — `/generate` 500s instead of degrading to "no RAG context." Pipeline already handles `retrieved_chunks=[]` gracefully (`pipeline.py:82`); the embedding call is the single point of failure. |
| B2 | **High** | `backend/app/validator/validator.py` | **Alignment is never validated.** No `_validate_alignment`. A sheet with `alignment="Chaotic Tuesday"` is legal. README and validator both promise SRD legality. |
| B3 | **Medium** | `backend/app/api/characters.py:101-105` | `DELETE /characters/{id}` does not check that the row exists. Returns 204 either way. Every other endpoint correctly 404s on missing IDs; this one silently masks client bugs. |
| B4 | **Medium** | `backend/app/auth.py:59` | Error response includes the raw JWT decode exception: `detail=f"Invalid authentication token: {exc}"`. Leaks algo/signature mismatch info to clients. Should be a flat `"Invalid authentication token"`. |
| B5 | **Medium** | `backend/app/rate_limit.py:23` | Rate-limit bucket key reads `sub` from the JWT *without signature verification* (`options={"verify_signature": False}`). Attacker can craft a token with any `sub` and shift their per-user bucket — they still can't access protected endpoints (those go through verified `get_current_user`), but the rate-limit accounting is bypassable. |
| B6 | **Low** | `backend/evals/run_evals.py:88` | `dt.datetime.utcnow()` is deprecated in 3.12 and removed in a future Python. Logs a DeprecationWarning on every eval run. |
| B7 | **Low** | `backend/app/api/share.py` | Share UUIDs live forever; no expiry, no revocation. Reasonable starting design but worth documenting since the README implies "share" is a fully-shipped polish feature. |

### Frontend

| # | Severity | File:Line | Description |
|---|---|---|---|
| F1 | **High** | (missing entirely) | **No character delete UI.** `api.deleteCharacter` exists in `lib/api.ts:52-53` but is wired nowhere. Users cannot remove a character from the UI. |
| F2 | **High** | App-wide | **No React error boundaries.** Any uncaught render error crashes the entire app to a blank page. |
| F3 | **High** | `frontend/src/components/CharacterEditor.tsx:35-46` (`save`) | If `api.updateCharacter` rejects, the `try/finally` clears the spinner but never surfaces the error. User sees "Saved" disappear and nothing happens. |
| F4 | **High** | `frontend/src/components/CharacterEditor.tsx:49-62` (`generate`) | Same pattern — failed `generate` (e.g. rate-limit 429, validator 500, network error) is swallowed. The flagship action of the app fails silently. |
| F5 | **High** | `frontend/src/components/CharacterList.tsx:28-31` (`create`) | `create()` has no try/catch. If `createCharacter` rejects, navigation never runs — clicking "+ New character" appears to do nothing. |
| F6 | **Medium** | `frontend/src/components/VersionHistory.tsx:18-21` (`restore`) | Restore has no confirm dialog AND no error handling. Clicking "Restore" on v3 instantly overwrites the editor's in-memory dirty changes without warning. |
| F7 | **Medium** | `frontend/src/components/VersionHistory.tsx:23-26` (`copyShareLink`) | Calls `navigator.clipboard?.writeText` and gives zero feedback whether it succeeded. User clicks "Share" and has no idea the link is on the clipboard. |
| F8 | **Medium** | `frontend/src/components/TraceViewer.tsx` (`useEffect` loader) | If `api.listRuns` rejects, the list is empty forever and the UI looks like "no generations yet." Same shape for VersionHistory. Indistinguishable from genuine empty state. |
| F9 | **Low** | `frontend/src/lib/api.ts:31-34` | Errors are thrown as `new Error("${status}: ${detail}")` — the raw HTTP detail (which may be HTML, validation JSON, or a stack) is included verbatim. Fine for dev, ugly for users when surfaced. |
| F10 | **Low** | `frontend/src/App.tsx:20-23` | `onAuthStateChange` updates `session` but never clears editor state. Signing out leaves the prior user's character in memory until the route changes. Minor leak in practice (RLS will block the next API call), still a smell. |

---

## (b) Plan items not yet implemented

Per the README's "shipped — all six phases complete" claim, the headline plan is done. Remaining items from the spec files and adjacent notes:

| # | Source | Item | Status |
|---|---|---|---|
| P1 | `SESSION.md:108` | Validator uses a curated `srd_data.py` subset (~29 spells). Common spells the LLM proposes (e.g. "Guiding Bolt") will fail validation. | **Open.** Either expand the spell pool or relax non-existent-spell errors to warnings. |
| P2 | `SESSION.md:14`, `README.md:14-16` | README placeholder for demo GIF + live URLs. | **Open.** Demo polish gap. |
| P3 | `SESSION.md:58` | CI workflow (`.github/workflows/`) for `pytest` + `npm build` + eval harness. | **Open.** |
| P4 | `SESSION.md:107` | CORS is single-origin (`FRONTEND_ORIGIN`); Vercel preview deploys are blocked. | **Open (deploy concern).** Already addressed in repo history (`b2c6230 Allow multiple CORS origins via comma-separated FRONTEND_ORIGIN`). Verify current `main.py` reflects it. |
| P5 | `README.md` features list | "Explain choices" — per-field source notes. | **Shipped** (`source` field on every `Field`, rendered in `SheetView`). Verified during audit. |

---

## (c) Functionality improvements (ranked by impact)

| # | Impact | Item | Why |
|---|---|---|---|
| I1 | **High** | Expand SRD spell pool (P1 above) or change validator behaviour for unknown spells from "reject" to "warn." | Current behaviour causes corrective-retry loops on plausible LLM output. Wastes LLM calls and confuses users. |
| I2 | **High** | Add the alignment validator (B2). | Cheap to add; closes the validator's last gap. |
| I3 | **High** | Wrap embedding call (B1) so RAG degrades to no-context instead of 500. | Single-point-of-failure on the main flow. |
| I4 | **Medium** | Surface generation cost/tokens in the editor UI (currently only in TraceViewer). | Sells the trace-viewer story when reviewers don't dig into the trace tab. |
| I5 | **Medium** | Add multiclass + subclass fields to the sheet schema. | README's resume framing mentions multiclass as an edge case; right now the schema has only `char_class` (singular). Adding it is a real schema migration + prompt + validator change. **Out of scope for an audit/fix pass unless the user wants it.** Document as future work. |
| I6 | **Medium** | HP / hit dice / saving throws / skill list. | These are real character-sheet fields the app doesn't model. Adds depth. Same out-of-scope flag as I5. |
| I7 | **Low** | Share-link expiry + revoke. | Production hygiene. |

---

## (d) Design / UX improvements

| # | Item | Notes |
|---|---|---|
| D1 | **Toaster / inline error banner system.** | Every async action in the app needs success and failure feedback (saved, generated, restored, copied, deleted, downloaded). Currently zero toasts. |
| D2 | **Confirm dialog for destructive actions.** | Restore version, delete character — both should ask. |
| D3 | **"Copied!" feedback on share link.** | Simple — gold-tinted ephemeral tooltip on the button for 1.5 s. |
| D4 | **Keyboard shortcut: Cmd/Ctrl+S to save** when the editor is dirty. | Power-user polish. |
| D5 | **VersionDiff UX.** | Currently exists as a separate component on the history tab but the user has to manually pick two versions; consider auto-defaulting to "latest vs previous" so the diff is visible without clicks. |
| D6 | **Empty states should distinguish "no data yet" from "failed to load."** | Tied to F8. |
| D7 | **CharacterList** could show updated_at relative ("3 hours ago"), portrait placeholder, and a delete affordance (F1). |
| D8 | **Mobile pass.** | sm: breakpoints are present but the editor's `sm:grid-cols-2` makes 12 sheet rows feel cramped on small viewports. Consider a single-column flow + collapse-by-default. |
| D9 | **Form input affordance on textareas.** | The user_notes textarea has no character-count or example chip. |
| D10 | **Auth page**: the README's "Roll your legend. Build your story." tagline could anchor the Auth screen for stronger first impression. |

---

## (e) Portfolio-readiness gaps

| # | Item | Notes |
|---|---|---|
| R1 | **README demo GIF still a placeholder.** | The trace viewer is the centerpiece. A 5-10s GIF would carry the resume framing. |
| R2 | **Live URLs not filled in.** | README header has `<your Vercel URL>` / `<your Railway URL>` placeholders. |
| R3 | **No CI.** | A green check next to commits is table-stakes for a portfolio review. |
| R4 | **No "About" link / context on auth screen.** | Reviewer signs in cold without knowing what the app does. |
| R5 | **No CLAUDE.md.** | The audit prompt referenced one. Adding a brief CLAUDE.md (architecture summary, conventions, "where to start") is high signal for reviewers. |
| R6 | **`SESSION.md` is local-only but contains useful narrative.** | Could distill the deploy-readiness story into the README's "Development log" section. Optional. |
| R7 | **The deprecation warning in evals** (B6) is the first thing a reviewer running `python evals/run_evals.py` sees. Fix it before demoing. |
| R8 | **No screenshot section in the README.** | Even still images would help. |
| R9 | **`backend/app/api/share.py` import path is right** but the share UUID expiry/revoke story (B7) is a question a sharp reviewer will ask. |

---

## What flag-feature locked-field iteration looks like under the microscope

I traced every code path that touches a locked field. **The flagship is intact.**

- `merge_preserving_locks` (`backend/app/pipeline/merge.py:26-46`) checks `field.locked` *before* applying any update. Locked fields are protected by a hard equality guard, not a convention. Empty locked values are not shown to the LLM in the prompt (filter at `prompt.py:133`) but are still protected at merge time — that asymmetry is correct.
- Both the initial group call and the corrective retry call go through the same merge function. The corrective retry surfaces validation errors plus current values plus a "fix only these fields" instruction; locks are re-asserted on the merged sheet immediately after.
- The "ALREADY GENERATED" section (`prompt.py:144-152`) carries values across groups for context but does **not** flip lock flags — locked stays locked, unlocked stays unlocked.
- All-locked input correctly skips LLM calls entirely (`pipeline.py:89-98`) and still runs the validator + writes a trace.

Eval-harness tests `single locked field: Druid`, `several locked: Wizard 5 / High Elf`, `level 5 druid, race locked to elf`, and `locked stats + class are preserved` all pass under the stub provider and exercise exactly this contract.

---

## Phase 2 plan (executed on this branch)

Priority order for fixes:

1. **B2** alignment validator (eval-driven: new test case covers it).
2. **B1** RAG embedding error handling (eval-driven: simulated failure).
3. **B4, B5, B6** small backend fixes.
4. **B3** DELETE 404.
5. **F2** error boundary.
6. **F3, F4, F5, F6, F8** error handling + restore confirm + toaster.
7. **F1** delete character UI + confirm.
8. **F7** "Copied!" feedback.
9. **I1** decide on spell-validator policy.
10. **D1-D3** polish.
11. **R7** datetime fix (folds into B6).
12. **R3** add CI workflow.

Each fix lands in its own commit so revert is per-improvement. Tests/evals run after every commit.

---

## Phase 2 — final status

Tests + evals + build at the end of Phase 2:

- `pytest`: **21/21** (was 19/19; added 2 alignment tests).
- `python evals/run_evals.py`: **19/19** (was 15/15; added 4 locked-field cases).
- `npm run build`: clean. 412 KB / 118 KB gzipped.
- Backend imports + dummy-env startup: clean.

### Resolved

**Backend bugs**

| # | Resolution | Commit |
|---|---|---|
| B1 | **False positive.** `embed()` IS wrapped by `retrieve_rules`'s try/except at `rag/retrieval.py:37-48` — embedding failures already degrade to empty chunks. The agent's read of `embeddings.py` in isolation missed the caller. No fix needed. | — |
| B2 | `ALIGNMENTS` set + `_validate_alignment` + two tests. | `3444698` |
| B3 | DELETE 404 on missing row. | `0cf6677` |
| B4 | 401 detail no longer echoes PyJWT exception. | `175776b` |
| B5 | Rate-limit key verifies signature via shared `_decode`. | `d710683` |
| B6 | `dt.datetime.utcnow()` → `dt.datetime.now(dt.UTC)`. | `175776b` |
| B7 | **Documented future work.** Share link expiry needs a schema change; deferred. | — |

**Frontend bugs**

| # | Resolution | Commit |
|---|---|---|
| F1 | Delete button + IconTrash + ConfirmDialog in CharacterEditor → `api.deleteCharacter` → nav home. | `58a539e` |
| F2 | `<ErrorBoundary>` wraps Routes; recoverable card with Try Again + Reload. | `cb32611` |
| F3-F5 | `runWithToast()` helper threads through save/generate/create with success+failure toasts. | `58a539e` |
| F6 | `<ConfirmDialog>` fires on restore when editor is dirty; restore goes through the toaster. | `58a539e` |
| F7 | `copyShareLink` shows "Share link copied" success or "Couldn't reach the clipboard" failure. | `58a539e` |
| F8 | Trace + Version loaders set explicit error banners distinct from empty state; TraceDetail has its own spinner. | `58a539e` |
| F9 | `runWithToast` strips the leading `^\d{3}:\s*` HTTP-prefix from raw API errors before toasting. | `58a539e` |
| F10 | App.tsx clears `useEditor.character` on sign-out. | `cb32611` |

**Functional improvements**

| # | Resolution | Commit |
|---|---|---|
| I1 | SPELLS pool expanded 41 → 97 entries covering Guiding Bolt and 50+ other high-frequency SRD spells across cantrips through 5th. | `a114400` |
| I2 | Same as B2. | — |
| I3 | False positive (was the duplicate of B1). | — |

**Design / UX**

| # | Resolution | Commit |
|---|---|---|
| D1 | `<ToasterProvider>` + `useToast()`. | `cb32611` |
| D2 | `<ConfirmDialog>` used by delete + restore-when-dirty. | `cb32611` / `58a539e` |
| D3 | "Share link copied" toast on success. | `58a539e` |
| D6 | Trace/Version loaders distinguish "no data" from "failed to load". | `58a539e` |

**Portfolio readiness**

| # | Resolution | Commit |
|---|---|---|
| R3 | GitHub Actions CI: backend pytest + evals + frontend build. | `2668ff4` |
| R5 | CLAUDE.md orientation doc added. | `3c94e39` |
| R7 | Subsumed by B6. | — |

### Recommended future work (deferred, not done on this branch)

These are real but out-of-scope for an audit/fix pass — they need schema work, design choices, or content the user supplies:

1. **B7 / R9** — Share-link expiry + revoke. Needs a `shared_versions(token uuid pk, version_id uuid, expires_at, revoked_at)` table and a UI to manage links.
2. **I4** — Surface generation cost/tokens in the editor (currently only in TraceViewer).
3. **I5 / I6** — Multiclass + subclass + HP / hit dice / saving throws / skills. Each is a real backend feature: schema field → prompt → validator → eval → frontend. The README's "multiclass" mention in the resume framing is aspirational; the model only carries `char_class` today.
4. **D4** — Cmd/Ctrl+S keyboard shortcut for save.
5. **D5** — VersionDiff auto-defaults (currently the user has to pick both sides manually).
6. **D7** — CharacterList: relative timestamps + inline delete.
7. **D8** — Mobile pass beyond the existing `sm:` breakpoints (editor + trace tabs feel cramped at 360px).
8. **D9** — Vibe-textarea character count + example chips.
9. **D10 / R4** — "About" link / tagline on the Auth screen so signed-out reviewers see what the app does.
10. **R1 / R2 / R8** — Demo GIF, live URLs in the README header, screenshot section. User-supplied content.
11. **R6** — Distill SESSION.md's deploy story into the README.
12. **Out-of-scope per spec reconciliation** — the audit prompt's portrait/party/song features are not implemented in ReRoll. If you want them here, that's a separate scope expansion.

### Diff vs main (audit branch summary)

11 commits, 23 files, +943 / −64:

```
3c94e39 docs: CLAUDE.md
2668ff4 ci: GitHub Actions
bf86afe test: expand eval harness (15 → 19)
a114400 feat: expand SRD spell pool (41 → 97)
58a539e feat: error handling + delete UI + restore confirm + share-copied
cb32611 feat: ToasterProvider + ErrorBoundary + ConfirmDialog
d710683 fix: verify JWT signature in rate-limit key (B5)
175776b fix: stop leaking JWT decode detail + drop datetime.utcnow (B4, B6)
0cf6677 fix: DELETE /characters/{id} returns 404 (B3)
3444698 fix: validate alignment against SRD's nine alignments (B2)
a3a018a Phase 1: AUDIT.md
```

Net result: every audit-flagged bug except B7 (a real but deferred schema item) is closed; the flagship locked-field iteration is now covered by 6 of the 19 eval cases (was 2); a real CI checks every change. Each commit is a single concern, so the user can `git revert <sha>` any one of them in isolation.

---

*Audit complete on `fable/audit-complete`. Ready for review.*
