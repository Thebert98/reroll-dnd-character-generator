import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useEditor } from "../store";
import { SHEET_FIELDS } from "../types";
import type { ValidationError } from "../types";
import { FieldRow } from "./FieldRow";
import { VersionHistory } from "./VersionHistory";
import { VersionDiff } from "./VersionDiff";
import { TraceViewer } from "./TraceViewer";

type Tab = "sheet" | "history" | "trace";

export function CharacterEditor() {
  const { id } = useParams<{ id: string }>();
  const character = useEditor((s) => s.character);
  const dirty = useEditor((s) => s.dirty);
  const setCharacter = useEditor((s) => s.setCharacter);
  const markClean = useEditor((s) => s.markClean);

  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [notes, setNotes] = useState("");
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [tab, setTab] = useState<Tab>("sheet");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!id) return;
    api.getCharacter(id).then(setCharacter);
  }, [id, setCharacter]);

  async function save() {
    if (!character) return;
    setSaving(true);
    try {
      await api.updateCharacter(character.id, {
        name: (character.sheet.name.value as string) || character.name,
        sheet: character.sheet,
      });
      markClean();
    } finally {
      setSaving(false);
    }
  }

  async function generate() {
    if (!character) return;
    setGenerating(true);
    try {
      // Persist current locks/values first so the server generates from them.
      await api.updateCharacter(character.id, { sheet: character.sheet });
      const result = await api.generate(character.id, { user_notes: notes });
      setCharacter(result.character);
      setErrors(result.validation_errors);
      setRefreshKey((k) => k + 1);
    } finally {
      setGenerating(false);
    }
  }

  if (!character) return <div>Loading…</div>;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          {(character.sheet.name.value as string) || "Untitled"}
        </h2>
        <div className="flex items-center gap-2">
          <button
            className="rounded border border-slate-700 px-3 py-2 text-sm hover:border-arcane"
            onClick={() => api.download(character.id, "json")}
          >
            Export JSON
          </button>
          <button
            className="rounded border border-slate-700 px-3 py-2 text-sm hover:border-arcane"
            onClick={() => api.download(character.id, "pdf")}
          >
            Export PDF
          </button>
          <button
            className="rounded bg-slate-700 px-4 py-2 text-sm font-medium disabled:opacity-50"
            onClick={save}
            disabled={!dirty || saving}
          >
            {saving ? "Saving…" : dirty ? "Save" : "Saved"}
          </button>
        </div>
      </div>

      <div className="mb-6 rounded-lg border border-arcane/40 bg-arcane/5 p-4">
        <p className="mb-2 text-sm text-slate-300">
          Lock the fields you want to keep, then regenerate the rest.
        </p>
        <textarea
          className="mb-2 w-full rounded bg-slate-900 px-3 py-2 text-sm"
          rows={2}
          placeholder="Optional theme / notes (e.g. 'a grim swamp witch who fears fire')"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button
          className="rounded bg-arcane px-4 py-2 font-medium disabled:opacity-50"
          onClick={generate}
          disabled={generating}
        >
          {generating ? "Conjuring…" : "✨ Generate unlocked fields"}
        </button>
      </div>

      {errors.length > 0 && (
        <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/10 p-4">
          <h3 className="mb-1 font-semibold text-red-300">
            Validation found {errors.length} issue{errors.length > 1 ? "s" : ""}
          </h3>
          <ul className="space-y-1 text-sm text-red-300">
            {errors.map((e, i) => (
              <li key={i}>
                <span className="font-mono text-xs text-red-400">[{e.field}]</span>{" "}
                {e.detail}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4 flex gap-2 border-b border-slate-800">
        {(["sheet", "history", "trace"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-sm capitalize ${
              tab === t
                ? "border-b-2 border-arcane text-arcane"
                : "text-slate-400"
            }`}
          >
            {t === "trace" ? "Trace viewer" : t}
          </button>
        ))}
      </div>

      {tab === "sheet" && (
        <div className="grid gap-3 sm:grid-cols-2">
          {SHEET_FIELDS.map((f) => (
            <FieldRow key={f} field={f} />
          ))}
        </div>
      )}
      {tab === "history" && (
        <div className="space-y-8">
          <VersionHistory key={refreshKey} characterId={character.id} />
          <div>
            <h3 className="mb-2 text-sm font-semibold text-slate-300">
              Compare versions
            </h3>
            <VersionDiff key={`diff-${refreshKey}`} characterId={character.id} />
          </div>
        </div>
      )}
      {tab === "trace" && (
        <TraceViewer key={refreshKey} characterId={character.id} />
      )}
    </div>
  );
}
