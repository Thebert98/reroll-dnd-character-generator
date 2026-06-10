import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useEditor } from "../store";
import { SHEET_FIELDS } from "../types";
import type { ValidationError } from "../types";
import { FieldRow } from "./FieldRow";
import { VersionHistory } from "./VersionHistory";
import { VersionDiff } from "./VersionDiff";
import { TraceViewer } from "./TraceViewer";
import { Button } from "./ui/Button";
import { ConfirmDialog } from "./ui/ConfirmDialog";
import { runWithToast, useToast } from "./ui/Toaster";
import { IconReRoll, IconExport, IconSave, IconTrash } from "./brand/icons";

type Tab = "sheet" | "history" | "trace";

export function CharacterEditor() {
  const { id } = useParams<{ id: string }>();
  const character = useEditor((s) => s.character);
  const dirty = useEditor((s) => s.dirty);
  const setCharacter = useEditor((s) => s.setCharacter);
  const markClean = useEditor((s) => s.markClean);

  const toaster = useToast();
  const nav = useNavigate();
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [notes, setNotes] = useState("");
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [tab, setTab] = useState<Tab>("sheet");
  const [refreshKey, setRefreshKey] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoadError(null);
    api.getCharacter(id).then(setCharacter).catch((err: Error) => {
      setLoadError(err.message.replace(/^\d{3}:\s*/, ""));
    });
  }, [id, setCharacter]);

  async function save() {
    if (!character) return;
    setSaving(true);
    const result = await runWithToast(
      toaster,
      api.updateCharacter(character.id, {
        name: (character.sheet.name.value as string) || character.name,
        sheet: character.sheet,
      }),
      { success: "Saved", failure: "Could not save" },
    );
    setSaving(false);
    if (result) markClean();
  }

  async function generate() {
    if (!character) return;
    setGenerating(true);
    // Save first so the server generates from current locks/values.
    const saved = await runWithToast(
      toaster,
      api.updateCharacter(character.id, { sheet: character.sheet }),
      { failure: "Could not save before re-roll" },
    );
    if (!saved) {
      setGenerating(false);
      return;
    }
    const result = await runWithToast(
      toaster,
      api.generate(character.id, { user_notes: notes }),
      { success: "Rolled the dice", failure: "Generation failed" },
    );
    setGenerating(false);
    if (!result) return;
    setCharacter(result.character);
    setErrors(result.validation_errors);
    setRefreshKey((k) => k + 1);
  }

  async function deleteCharacter() {
    if (!character) return;
    setConfirmDelete(false);
    const result = await runWithToast(
      toaster,
      api.deleteCharacter(character.id),
      { success: "Character banished", failure: "Could not delete character" },
    );
    if (result !== undefined) {
      setCharacter(null);
      nav("/");
    }
  }

  if (loadError)
    return (
      <div className="rounded-xl border border-brand-red/40 bg-brand-red/10 p-4 text-sm text-brand-red">
        Could not load character — {loadError}
      </div>
    );
  if (!character) return <div>Loading…</div>;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-heading text-2xl font-bold text-brand-stone">
          {(character.sheet.name.value as string) || "Untitled"}
        </h2>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={() =>
              runWithToast(toaster, api.download(character.id, "json"), {
                failure: "JSON export failed",
              })
            }
          >
            <IconExport size={14} /> JSON
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() =>
              runWithToast(toaster, api.download(character.id, "pdf"), {
                failure: "PDF export failed",
              })
            }
          >
            <IconExport size={14} /> PDF
          </Button>
          <Button
            variant={dirty ? "primary" : "secondary"}
            onClick={save}
            disabled={!dirty || saving}
          >
            <IconSave size={14} /> {saving ? "Saving…" : dirty ? "Save" : "Saved"}
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => setConfirmDelete(true)}
            title="Delete this character"
          >
            <IconTrash size={14} /> Delete
          </Button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmDelete}
        title="Delete this character?"
        body="This cannot be undone. Version history and trace logs will also be removed."
        confirmLabel="Delete"
        confirmVariant="danger"
        onConfirm={deleteCharacter}
        onCancel={() => setConfirmDelete(false)}
      />

      <div className="mb-6 rounded-xl border border-brand-arcane/40 bg-brand-arcane/5 p-4">
        <p className="mb-2 font-heading text-sm text-brand-stone/80">
          🔒 Lock the fields you want to keep, then{" "}
          <span className="text-brand-gold">re-roll</span> the rest.
        </p>
        <textarea
          className="mb-3 w-full rounded-lg border border-ink-600 bg-ink-900 px-3 py-2 text-sm outline-none focus:border-brand-gold focus:ring-1 focus:ring-brand-gold/60"
          rows={2}
          placeholder="Optional theme / notes (e.g. 'a grim swamp witch who fears fire')"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <Button variant="magic" onClick={generate} disabled={generating}>
          <IconReRoll size={16} />
          {generating ? "Rolling the dice…" : "Re-Roll unlocked fields"}
        </Button>
      </div>

      {errors.length > 0 && (
        <div className="mb-6 rounded-xl border border-brand-red/40 bg-brand-red/10 p-4">
          <h3 className="mb-1 font-heading font-semibold text-brand-red">
            Validation found {errors.length} issue{errors.length > 1 ? "s" : ""}
          </h3>
          <ul className="space-y-1 text-sm text-brand-red/90">
            {errors.map((e, i) => (
              <li key={i}>
                <span className="font-mono text-xs text-brand-ember">[{e.field}]</span>{" "}
                {e.detail}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4 flex gap-2 border-b border-ink-600">
        {(["sheet", "history", "trace"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 font-heading text-sm capitalize transition-colors ${
              tab === t
                ? "border-b-2 border-brand-gold text-brand-gold"
                : "text-brand-stone/50 hover:text-brand-stone"
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
            <h3 className="mb-2 font-heading text-sm font-semibold text-brand-stone">
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
