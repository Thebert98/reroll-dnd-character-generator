import type { CharacterSheet } from "../types";
import { FIELD_LABELS } from "../types";
import { useEditor } from "../store";
import { Badge } from "./ui/Badge";
import { IconLock, IconUnlock } from "./brand/icons";

interface Props {
  field: keyof CharacterSheet;
}

// Shared input styling: dark ink field with a gold focus ring (style book).
const INPUT =
  "w-full rounded-lg border border-ink-600 bg-ink-900 px-2 py-1 text-sm outline-none " +
  "focus:border-brand-gold focus:ring-1 focus:ring-brand-gold/60";

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
      className={`rounded-xl border p-3 transition-colors ${
        locked
          ? "border-brand-gold/70 bg-brand-gold/5 shadow-gold"
          : "border-ink-600/80 bg-ink-700/40"
      }`}
    >
      <div className="mb-1 flex items-center justify-between">
        <label className="flex items-center gap-2 font-heading text-sm font-medium text-brand-stone/90">
          {FIELD_LABELS[field]}
          {f.source && <Badge kind="ai" />}
        </label>
        <button
          onClick={() => toggleLock(field)}
          title={locked ? "Locked — AI will not change this" : "Unlocked — AI may re-roll this"}
          className={`flex items-center gap-1 text-xs font-heading transition-colors ${
            locked ? "text-brand-gold" : "text-brand-stone/40 hover:text-brand-stone/70"
          }`}
        >
          {locked ? <IconLock size={13} /> : <IconUnlock size={13} />}
          {locked ? "Locked" : "Unlocked"}
        </button>
      </div>
      <FieldInput field={field} />
      {f.source && (
        <p className="mt-1 text-xs italic text-brand-stone/45">why: {f.source}</p>
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
            <div className="text-[10px] uppercase text-brand-gold/70">{k}</div>
            <input
              className={`${INPUT} px-1 text-center`}
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
        className={INPUT}
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
        className={INPUT}
        rows={3}
        value={(value as string) || ""}
        onChange={(e) => setFieldValue(field, e.target.value)}
      />
    );
  }

  if (field === "level") {
    return (
      <input
        className={`${INPUT} w-24`}
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
      className={INPUT}
      type="text"
      value={(value as string) || ""}
      onChange={(e) => setFieldValue(field, e.target.value)}
    />
  );
}
