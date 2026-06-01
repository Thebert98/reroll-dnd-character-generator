import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { RunSummary, TraceRun } from "../types";

/** The trace viewer: for any generation run, render the locked constraints,
 *  retrieved chunks, the assembled prompt, raw model output, validation
 *  results, and token/cost/latency. This is the demo centerpiece. */
export function TraceViewer({ characterId }: { characterId: string }) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selected, setSelected] = useState<TraceRun | null>(null);

  useEffect(() => {
    api.listRuns(characterId).then(setRuns);
  }, [characterId]);

  async function open(runId: string) {
    setSelected(await api.getRun(runId));
  }

  if (runs.length === 0)
    return <p className="text-sm text-slate-400">No generations yet.</p>;

  return (
    <div className="grid gap-4 md:grid-cols-[16rem,1fr]">
      <ul className="space-y-1">
        {runs.map((r) => {
          const ok = (r.validation_errors?.length ?? 0) === 0;
          return (
            <li key={r.id}>
              <button
                onClick={() => open(r.id)}
                className={`w-full rounded border px-2 py-1 text-left text-xs ${
                  selected?.id === r.id ? "border-arcane" : "border-slate-800"
                }`}
              >
                <span className={ok ? "text-emerald-400" : "text-red-400"}>
                  {ok ? "✓ valid" : "✗ invalid"}
                </span>{" "}
                · {r.model} · {r.latency_ms ?? "?"}ms
                <div className="text-slate-500">
                  {r.created_at?.slice(0, 19).replace("T", " ")}
                </div>
              </button>
            </li>
          );
        })}
      </ul>
      <div>{selected ? <TraceDetail run={selected} /> : <Hint />}</div>
    </div>
  );
}

function Hint() {
  return (
    <p className="text-sm text-slate-400">Select a run to inspect its trace.</p>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <details open className="rounded border border-slate-800 p-3">
      <summary className="cursor-pointer text-sm font-semibold text-slate-200">
        {title}
      </summary>
      <div className="mt-2 text-xs">{children}</div>
    </details>
  );
}

function Pre({ data }: { data: unknown }) {
  return (
    <pre className="max-h-64 overflow-auto rounded bg-slate-900 p-2 text-[11px] text-slate-300">
      {typeof data === "string" ? data : JSON.stringify(data, null, 2)}
    </pre>
  );
}

function TraceDetail({ run }: { run: TraceRun }) {
  const ok = (run.validation_errors?.length ?? 0) === 0;
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3 text-xs text-slate-400">
        <span>model: {run.model}</span>
        <span>latency: {run.latency_ms ?? "?"}ms</span>
        <span>
          tokens: {run.input_tokens ?? 0} in / {run.output_tokens ?? 0} out
        </span>
        <span>cost: ${run.cost_usd ?? 0}</span>
      </div>

      <Section title={`Locked fields (${run.locked_fields.length})`}>
        {run.locked_fields.length ? (
          <div className="flex flex-wrap gap-1">
            {run.locked_fields.map((f) => (
              <span key={f} className="rounded bg-arcane/20 px-2 py-0.5 text-arcane">
                🔒 {f}
              </span>
            ))}
          </div>
        ) : (
          <span className="text-slate-500">none — generated from scratch</span>
        )}
      </Section>

      <Section title={`Retrieved SRD chunks (${run.retrieved_chunks?.length ?? 0})`}>
        {run.retrieved_chunks?.length ? (
          <ul className="space-y-2">
            {run.retrieved_chunks.map((c, i) => (
              <li key={i} className="rounded bg-slate-900 p-2">
                <div className="mb-1 flex justify-between text-slate-400">
                  <span>{c.section ?? "SRD"}</span>
                  {c.score != null && <span>score {c.score.toFixed(3)}</span>}
                </div>
                <div className="text-slate-300">{c.text ?? c.content}</div>
              </li>
            ))}
          </ul>
        ) : (
          <span className="text-slate-500">no retrieval (RAG added in Phase 4)</span>
        )}
      </Section>

      <Section title="Validation results">
        {ok ? (
          <span className="text-emerald-400">✓ All rules passed.</span>
        ) : (
          <ul className="space-y-1">
            {run.validation_errors!.map((e, i) => (
              <li key={i} className="text-red-400">
                ✗ [{e.rule}] {e.detail}
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Assembled prompt">
        <Pre data={run.prompt ?? "(not stored)"} />
      </Section>

      <Section title="Raw model output (before merge)">
        <Pre data={run.raw_output ?? {}} />
      </Section>
    </div>
  );
}
