import type { CharacterSheet } from "../types";
import { SHEET_FIELDS, FIELD_LABELS } from "../types";

const ABILITIES = ["str", "dex", "con", "int", "wis", "cha"];

function format(value: unknown): string {
  if (value == null || value === "") return "—";
  if (Array.isArray(value)) return value.length ? value.join(", ") : "—";
  if (typeof value === "object")
    return Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${k.toUpperCase()} ${v}`)
      .join("  ");
  return String(value);
}

function modifier(score: number): string {
  const m = Math.floor((score - 10) / 2);
  return m >= 0 ? `+${m}` : `${m}`;
}

/** Ability-score blocks, styled after the style book's "Abilities" panel. */
function AbilityScores({ stats }: { stats: Record<string, number> }) {
  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
      {ABILITIES.map((ab) => {
        const score = Number(stats?.[ab] ?? 0);
        return (
          <div
            key={ab}
            className="rounded-lg border border-ink-600/80 bg-ink-700/50 py-2 text-center"
          >
            <div className="text-[10px] font-semibold uppercase tracking-wide text-brand-gold/80">
              {ab}
            </div>
            <div className="font-heading text-xl font-bold text-brand-stone">
              {score || "—"}
            </div>
            <div className="text-xs text-brand-stone/50">
              {score ? modifier(score) : ""}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** Read-only render of a sheet, including each field's `source` ("explain
 *  choices") — used by the public share page. */
export function SheetView({ sheet }: { sheet: CharacterSheet }) {
  const stats = (sheet.stats?.value as Record<string, number>) || {};
  const hasStats = ABILITIES.some((a) => stats[a]);

  return (
    <div className="space-y-4">
      {hasStats && (
        <div className="rounded-xl border border-ink-600/80 bg-ink-800/40 p-4">
          <div className="mb-2 font-heading text-xs font-semibold uppercase tracking-wide text-brand-stone/60">
            {FIELD_LABELS.stats}
          </div>
          <AbilityScores stats={stats} />
          {sheet.stats?.source && (
            <div className="mt-2 text-xs italic text-brand-stone/50">
              why: {sheet.stats.source}
            </div>
          )}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {SHEET_FIELDS.filter((f) => f !== "stats").map((f) => {
          const field = sheet[f];
          return (
            <div
              key={f}
              className="rounded-xl border border-ink-600/80 bg-ink-700/30 p-3"
            >
              <div className="font-heading text-xs font-semibold uppercase tracking-wide text-brand-stone/60">
                {FIELD_LABELS[f]}
              </div>
              <div className="mt-1 text-sm text-brand-stone">
                {format(field?.value)}
              </div>
              {field?.source && (
                <div className="mt-1 text-xs italic text-brand-stone/50">
                  why: {field.source}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
