import type { CharacterSheet } from "../types";
import { FIELD_LABELS } from "../types";
import { useEditor } from "../store";

interface Props {
  field: keyof CharacterSheet;
}

/** Render a single sheet field as an editable control plus a lock toggle.
 *  The lock toggle is the heart of the product: a locked field becomes a hard
 *  constraint the AI may not change. */
export function FieldRow({ field }: Props) {
  const character = useEditor((s) => s.character);
  const toggleLock = useEditor((s) => s.toggleLock);
  if (!character) return null;

  const f = character.sheet[field];
  const locked = f.locked;

  return (
    <div
      className={`rounded-lg border p-3 ${
        locked ? "border-arcane bg-arcane/5" : "border-slate-800"
      }`}
    >
      <div className="mb-1 flex items-center justify-between">
        <label className="text-sm font-medium text-slate-300">
          {FIELD_LABELS[field]}
        </label>
        <button
          onClick={() => toggleLock(field)}
          title={locked ? "Locked — AI will not change this" : "Unlocked"}
          className={`text-xs ${locked ? "text-arcane" : "text-slate-500"}`}
        >
          {locked ? "🔒 Locked" : "🔓 Unlocked"}
        </button>
      </div>
      <FieldInput field={field} />
      {f.source && (
        <p className="mt-1 text-xs italic text-slate-500">why: {f.source}</p>
      )}
    </div>
  );
}

function FieldInput({ field }: Props) {
  const character = useEditor((s) => s.character)!;
  const setFieldValue = useEditor((s) => s.setFieldValue);
  const value = character.sheet[field].value;

  if (field === "stats") {
    const stats = (value as Record<string, number>) || {};
    const keys = ["str", "dex", "con", "int", "wis", "cha"];
    return (
      <div className="grid grid-cols-6 gap-1">
        {keys.map((k) => (
          <div key={k} className="text-center">
            <div className="text-[10px] uppercase text-slate-500">{k}</div>
            <input
              className="w-full rounded bg-slate-900 px-1 py-1 text-center"
              type="number"
              value={stats[k] ?? ""}
              onChange={(e) =>
                setFieldValue("stats", {
                  ...stats,
                  [k]: Number(e.target.value),
                })
              }
            />
          </div>
        ))}
      </div>
    );
  }

  if (["proficiencies", "spells", "equipment"].includes(field)) {
    const list = Array.isArray(value) ? (value as string[]) : [];
    return (
      <textarea
        className="w-full rounded bg-slate-900 px-2 py-1 text-sm"
        rows={2}
        placeholder="One per line"
        value={list.join("\n")}
        onChange={(e) =>
          setFieldValue(
            field,
            e.target.value.split("\n").filter((s) => s.trim())
          )
        }
      />
    );
  }

  if (["backstory", "personality"].includes(field)) {
    return (
      <textarea
        className="w-full rounded bg-slate-900 px-2 py-1 text-sm"
        rows={3}
        value={(value as string) || ""}
        onChange={(e) => setFieldValue(field, e.target.value)}
      />
    );
  }

  if (field === "level") {
    return (
      <input
        className="w-24 rounded bg-slate-900 px-2 py-1"
        type="number"
        min={1}
        max={20}
        value={(value as number) ?? ""}
        onChange={(e) => setFieldValue(field, Number(e.target.value))}
      />
    );
  }

  return (
    <input
      className="w-full rounded bg-slate-900 px-2 py-1"
      type="text"
      value={(value as string) || ""}
      onChange={(e) => setFieldValue(field, e.target.value)}
    />
  );
}
