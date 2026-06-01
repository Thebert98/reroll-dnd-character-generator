import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useEditor } from "../store";
import { SHEET_FIELDS } from "../types";
import { FieldRow } from "./FieldRow";

export function CharacterEditor() {
  const { id } = useParams<{ id: string }>();
  const character = useEditor((s) => s.character);
  const dirty = useEditor((s) => s.dirty);
  const setCharacter = useEditor((s) => s.setCharacter);
  const markClean = useEditor((s) => s.markClean);
  const [saving, setSaving] = useState(false);

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

  if (!character) return <div>Loading…</div>;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          {(character.sheet.name.value as string) || "Untitled"}
        </h2>
        <button
          className="rounded bg-arcane px-4 py-2 font-medium disabled:opacity-50"
          onClick={save}
          disabled={!dirty || saving}
        >
          {saving ? "Saving…" : dirty ? "Save" : "Saved"}
        </button>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        {SHEET_FIELDS.map((f) => (
          <FieldRow key={f} field={f} />
        ))}
      </div>
    </div>
  );
}
