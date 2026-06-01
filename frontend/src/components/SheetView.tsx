import type { CharacterSheet } from "../types";
import { SHEET_FIELDS, FIELD_LABELS } from "../types";

function format(value: unknown): string {
  if (value == null || value === "") return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  if (typeof value === "object")
    return Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${k.toUpperCase()} ${v}`)
      .join("  ");
  return String(value);
}

/** Read-only render of a sheet, including each field's `source` ("explain
 *  choices") — used by the public share page. */
export function SheetView({ sheet }: { sheet: CharacterSheet }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {SHEET_FIELDS.map((f) => {
        const field = sheet[f];
        return (
          <div key={f} className="rounded-lg border border-slate-800 p-3">
            <div className="text-xs font-semibold uppercase text-slate-400">
              {FIELD_LABELS[f]}
            </div>
            <div className="mt-1 text-sm text-slate-100">
              {format(field?.value)}
            </div>
            {field?.source && (
              <div className="mt-1 text-xs italic text-slate-500">
                why: {field.source}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
